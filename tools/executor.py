from datetime import datetime
import json
from sqlalchemy.orm import Session
from models.task import Task as TaskModel
from services import tasks as tasks_service


def execute_tool(tool_name: str, tool_input: dict, db: Session, user_id: int) -> str:
    if tool_name == "get_user_tasks":
        tasks = tasks_service.list_tasks(db, user_id)

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

        new_task = tasks_service.create_task(
            db=db,
            user_id=user_id,
            title=title.strip(),
            description=description.strip() if description else None,
            priority=priority,
            due_date=due_date,
        )

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

        is_deleted = tasks_service.delete_task(db, user_id, task_id)
        if not is_deleted:
            return json.dumps(
                {"error": f"No task found with ID {task_id} for this user"}
            )

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

        # Конвертуємо due_date з рядка в datetime ДО передачі в service
        fields = dict(tool_input)  # копія, щоб не псувати оригінал
        fields.pop("id", None)  # id не оновлюємо, тільки шукаємо

        if "due_date" in fields:
            due_date_str = fields["due_date"]
            fields["due_date"] = (
                datetime.fromisoformat(due_date_str) if due_date_str else None
            )

        task = tasks_service.update_task(db, user_id, task_id, fields)
        if not task:
            return json.dumps({"error": f"No task found with ID {task_id}"})

        return json.dumps(
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_done": task.is_done,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "message": f"Task {task_id} updated",
            },
            default=str,
            ensure_ascii=False,
        )

    raise ValueError(f"Unknown tool: {tool_name}")
