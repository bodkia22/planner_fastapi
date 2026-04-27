from fastapi import APIRouter, Depends, HTTPException
from schemas.task import TaskCreate, TaskUpdate

import database
from utils.jwt import get_current_user

from services import tasks as tasks_service

router = APIRouter()


@router.post("/tasks")
def create_task(
    task: TaskCreate,
    db=Depends(database.get_db),
    current_user=Depends(get_current_user),
):
    new_task = tasks_service.create_task(
        db=db,
        user_id=current_user.id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        due_date=task.due_date,
    )
    return new_task


@router.get("/tasks")
def get_tasks(db=Depends(database.get_db), current_user=Depends(get_current_user)):
    return tasks_service.list_tasks(db, current_user.id)


@router.get("/tasks/{task_id}")
def get_task(
    task_id: int, db=Depends(database.get_db), current_user=Depends(get_current_user)
):
    task = tasks_service.get_task(db, current_user.id, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/tasks/{task_id}")
def delete_task(
    task_id: int, db=Depends(database.get_db), current_user=Depends(get_current_user)
):
    deleted = tasks_service.delete_task(db, current_user.id, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"detail": "Task deleted"}


@router.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db=Depends(database.get_db),
    current_user=Depends(get_current_user),
):
    updated_task = tasks_service.update_task(
        db=db,
        user_id=current_user.id,
        task_id=task_id,
        fields=task_update.model_dump(exclude_unset=True),
    )
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task
