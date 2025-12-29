from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Annotated, List
from sqlmodel import select, SQLModel, Field
from database import SessionDep
from .user_manager import User, get_current_user, oauth2_scheme

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

class TaskUpdate(SQLModel):
    name: str | None = None
    priority: str | None = None
    date: str | None = None
    status: str | None = None
    
def verify_user(session,token: Annotated[str, Depends(oauth2_scheme)]):
    current_user = get_current_user(session,token)
    user =  session.exec(select(User).where(User.name == current_user.name)).first()
    if user is None:
        raise HTTPException(status_code=403, detail="User not found")
    return user.id

@router.post("/{user_id}", response_model=TaskPublic)
def create_task(task: Taskbase, session: SessionDep, token: Annotated[str, Depends(oauth2_scheme)]):
    user = verify_user(session,token)
    if user != task.user_id:
        raise HTTPException(status_code=404, detail="Invalid User")

    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@router.get("/{user_id}", response_model=List[TaskPublic])
def read_task(user_id,
    session: SessionDep,token: Annotated[str, Depends(oauth2_scheme)],
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    user = verify_user(session,token)
    if user != user_id:
        raise HTTPException(status_code=403, detail="Invalid User")
    tasks = list(session.exec(select(Task).where(Task.user_id == user_id).offset(offset).limit(limit)).all())
    return tasks

@router.delete("/{user_id}/{task_id}")
def delete_task(task_id: int, user_id: int, token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep):
    user = verify_user(session,token)
    if user!= user_id:
        raise HTTPException(status_code=403, detail="Invalid User")

    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"ok": True}

@router.put("/{user_id}/{task_id}", response_model=TaskPublic)
def update_task(task_id: int, user_id:int, task: TaskUpdate, token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep):
    user = verify_user(session,token)
    if user!= user_id:
        raise HTTPException(status_code=403, detail="Invalid User")

    task_old = session.get(Task, task_id)
    if not task_old:
        raise HTTPException(status_code=404, detail="Task not found")
    task_dict = task.model_dump(exclude_unset=True)
    task_old.sqlmodel_update(task_dict)
    session.add(task_old)
    session.commit()
    session.refresh(task_old)
    return task_old
