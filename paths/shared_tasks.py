from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Annotated, List
from sqlmodel import select, SQLModel, Field
from database import SessionDep
from .user_manager import get_current_user, oauth2_scheme

router = APIRouter()

class SharedTaskbase(SQLModel):
    name: str
    priority: str = Field(index=True, default="Normal")
    date: str = Field(index=True)
    status: str = Field(default="new")
    created_by: str | None = None
    workspace_id: int = Field(index=True)

class SharedTask(SharedTaskbase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class SharedTaskPublic(SharedTaskbase):
    id: int

class SharedTaskUpdate(SQLModel):
    name: str | None = None
    priority: str | None = None
    date: str | None = None
    status: str | None = None
    
@router.post("/{workspace_id}", response_model=SharedTaskPublic)
def create_task(task: SharedTaskbase, token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep):
    current_user = get_current_user(session,token)
    task.created_by = current_user.name
    db_task = SharedTask.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@router.get("/{workspace_id}", response_model=List[SharedTaskPublic])
def read_task(workspace_id,
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    tasks = list(session.exec(select(SharedTask).where(SharedTask.workspace_id == workspace_id).offset(offset).limit(limit)).all())
    return tasks

@router.delete("/{workspace_id}/{task_id}")
def delete_task(task_id: int, session: SessionDep):
    task = session.get(SharedTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="SharedTask not found")
    session.delete(task)
    session.commit()
    return {"ok": True}

@router.put("/{workspace_id}/{task_id}", response_model=SharedTaskPublic)
def update_task(task_id: int, task: SharedTaskUpdate, session: SessionDep):
    task_old = session.get(SharedTask, task_id)
    if not task_old:
        raise HTTPException(status_code=404, detail="Task not found")
    task_dict = task.model_dump(exclude_unset=True)
    task_old.sqlmodel_update(task_dict)
    session.add(task_old)
    session.commit()
    session.refresh(task_old)
    return task_old
