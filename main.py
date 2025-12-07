from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import create_db_and_tables
from paths import task_manager, user_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # create tables before app starts
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(task_manager.router, prefix="/tasks", tags=["tasks"])
app.include_router(user_manager.router, prefix="/users", tags=["users"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Task Manager API"}
