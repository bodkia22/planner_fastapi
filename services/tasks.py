from sqlalchemy.orm import Session
from datetime import datetime
from models.task import Task as TaskModel

ALLOWED_UPDATE_FIELDS = {"title", "description", "priority", "due_date", "is_done"}


def list_tasks(db: Session, user_id: int) -> list[TaskModel]:
    return db.query(TaskModel).filter(TaskModel.user_id == user_id).all()


def create_task(
    db: Session,
    user_id: int,
    *,
    title: str,
    description: str | None = None,
    priority: int = 0,
    due_date: datetime | None = None,
) -> TaskModel:
    task = TaskModel(
        user_id=user_id,
        title=title,
        description=description,
        priority=priority,
        due_date=due_date,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task(db: Session, user_id: int, task_id: int) -> TaskModel | None:
    return (
        db.query(TaskModel)
        .filter(
            TaskModel.id == task_id,
            TaskModel.user_id == user_id,
        )
        .first()
    )


def update_task(
    db: Session,
    user_id: int,
    task_id: int,
    fields: dict,
) -> TaskModel | None:
    task = get_task(db, user_id, task_id)
    if not task:
        return None

    for field, value in fields.items():
        if field in ALLOWED_UPDATE_FIELDS:
            setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, user_id: int, task_id: int) -> bool:
    task = get_task(db, user_id, task_id)
    if not task:
        return False
    db.delete(task)
    db.commit()
    return True
