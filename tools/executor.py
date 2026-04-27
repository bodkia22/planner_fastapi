from datetime import datetime
import json
from sqlalchemy.orm import Session
from models.task import Task as TaskModel


def execute_tool(tool_name: str, tool_input: dict, db: Session, user_id: int) -> str:
    if tool_name == "get_user_tasks":
        tasks = db.query(TaskModel).filter(TaskModel.user_id == user_id).all()

        # Серіалізуємо у JSON-сумісний список dict-ів
        result = [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "is_done": t.is_done,
                "priority": t.priority,
                "due_date": t.due_date.isoformat() if t.due_date else None,  # type: ignore
            }
            for t in tasks
        ]

        return json.dumps(result, default=str, ensure_ascii=False)

    elif tool_name == "create_task":
        title = tool_input.get("title")
        description = tool_input.get("description")
        priority = tool_input.get("priority", 0)

        due_date_str = tool_input.get("due_date")
        due_date = datetime.fromisoformat(due_date_str) if due_date_str else None

        if not title or not title.strip():
            return json.dumps({"error": "Title is required and cannot be empty"})

        new_task = TaskModel(
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        return json.dumps(
            {
                "id": new_task.id,
                "title": new_task.title,
                "description": new_task.description,
                "is_done": new_task.is_done,
                "priority": new_task.priority,
                "due_date": new_task.due_date.isoformat() if new_task.due_date else None,  # type: ignore
            },
            default=str,
            ensure_ascii=False,
        )

    elif tool_name == "delete_task":
        task_id = tool_input.get("id")
        if task_id is None:
            return json.dumps({"error": "Task ID is required for deletion"})

        task = (
            db.query(TaskModel)
            .filter(TaskModel.id == task_id, TaskModel.user_id == user_id)
            .first()
        )
        if not task:
            return json.dumps(
                {"error": f"No task found with ID {task_id} for this user"}
            )

        db.delete(task)
        db.commit()

        return json.dumps(
            {
                "success": True,
                "deleted_id": task_id,
                "message": f"Task {task_id} deleted",
            }
        )

    elif tool_name == "update_task":
        task_id = tool_input.get("id")
        if task_id is None:
            return json.dumps({"error": "Task ID is required for update"})

        task = (
            db.query(TaskModel)
            .filter(TaskModel.id == task_id, TaskModel.user_id == user_id)
            .first()
        )
        if not task:
            return json.dumps(
                {"error": f"No task found with ID {task_id} for this user"}
            )

        # Оновлюємо поля, якщо вони є у вхідних даних
        if "title" in tool_input:
            task.title = tool_input["title"]
        if "description" in tool_input:
            task.description = tool_input["description"]
        if "priority" in tool_input:
            task.priority = tool_input["priority"]
        if "due_date" in tool_input:
            due_date_str = tool_input.get("due_date")
            task.due_date = (
                datetime.fromisoformat(due_date_str) if due_date_str else None
            )
        if "is_done" in tool_input:
            task.is_done = tool_input["is_done"]

        db.commit()
        db.refresh(task)

        return json.dumps(
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_done": task.is_done,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,  # type: ignore
                "message": f"Task {task_id} updated",
            },
            default=str,
            ensure_ascii=False,
        )

    raise ValueError(f"Unknown tool: {tool_name}")
