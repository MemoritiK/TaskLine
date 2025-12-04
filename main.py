from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from contextlib import asynccontextmanager

class Taskbase(SQLModel):
    name: str 
    priority: str = Field(index=True, default="Normal")
    date: str = Field(index=True)
    
class Task(Taskbase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class TaskPublic(Taskbase):
    id: int

class TaskUpdate(Taskbase):
    name: str 
    priority: str = Field(index=True, default="Normal")
    date: str = Field(index=True)
    
sqlite_file_name = "task.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager # executes before app starts
async def lifespan(app: FastAPI):
    # Create table
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Task Manager API"}

@app.post("/tasks/") # create new tasks
def create_task(task: Taskbase, session: SessionDep):
    db_task = Task.model_validate(task) # generate id
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task
    
@app.get("/tasks/",response_model=list[TaskPublic])
def read_task(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    tasks = list(session.exec(select(Task).offset(offset).limit(limit)).all())
    return tasks
    
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, session: SessionDep):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"ok": True}

@app.put("/tasks/{task_id}", response_model=TaskPublic)
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
    