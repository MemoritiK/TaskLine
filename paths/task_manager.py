from fastapi import APIRouter, HTTPException, Query
from typing import Annotated, List
from sqlmodel import select, SQLModel, Field
from database import SessionDep

router = APIRouter()

class Taskbase(SQLModel):
    name: str
    priority: str = Field(index=True, default="Normal")
    date: str = Field(index=True)
    status: str = Field(default="new")
    user_id: int = Field(index=True)

class Task(Taskbase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class TaskPublic(Taskbase):
    id: int

class TaskUpdate(Taskbase):
    name: str | None = None
    priority: str | None = None
    date: str | None = None
    status: str | None = None

@router.post("/{user_id}", response_model=TaskPublic)
def create_task(task: Taskbase, session: SessionDep):
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@router.get("/{user_id}", response_model=List[TaskPublic])
def read_task(user_id,
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    tasks = list(session.exec(select(Task).where(Task.user_id == user_id).offset(offset).limit(limit)).all())
    return tasks

@router.delete("/{user_id}/{task_id}")
def delete_task(task_id: int, session: SessionDep):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"ok": True}

@router.put("/{user_id}/{task_id}", response_model=TaskPublic)
def update_task(task_id: int, task: TaskUpdate, session: SessionDep):
    task_old = session.get(Task, task_id)
    if not task_old:
        raise HTTPException(status_code=404, detail="Task not found")
    task_dict = task.model_dump(exclude_unset=True)
    task_old.sqlmodel_update(task_dict)
    session.add(task_old)
    session.commit()
    session.refresh(task_old)
    return task_old
