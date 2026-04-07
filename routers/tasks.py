from fastapi import APIRouter, Depends, HTTPException
from schemas.task import Task, TaskCreate, TaskUpdate
from models.task import Task as TaskModel

import database

router = APIRouter()


@router.post("/tasks")
def create_task(task: TaskCreate, db=Depends(database.get_db)):
    new_task = TaskModel(
        title=task.title, description=task.description, priority=task.priority
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@router.get("/tasks")
def get_tasks(db=Depends(database.get_db)):
    return db.query(TaskModel).all()


@router.get("/tasks/{task_id}")
def get_task(task_id: int, db=Depends(database.get_db)):
    db_task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db=Depends(database.get_db)):
    db_task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return {"detail": "Task deleted"}


@router.put("/tasks/{task_id}")
def update_task(task_id: int, task_update: TaskUpdate, db=Depends(database.get_db)):
    db_task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update the task with the new values
    if task_update.title is not None:
        db_task.title = task_update.title
    if task_update.description is not None:
        db_task.description = task_update.description
    if task_update.is_done is not None:
        db_task.is_done = task_update.is_done

    db.commit()
    db.refresh(db_task)
    return db_task
