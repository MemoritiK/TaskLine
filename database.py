from typing import Annotated
from sqlmodel import SQLModel, Session
from fastapi import Depends
from sqlalchemy import create_engine
import os

pssd = os.getenv("NEON_TOKEN")
sqlite_file_name = "task.db"
#sqlite_url = f"sqlite:///{sqlite_file_name}"
sqlite_url = f'postgresql://{pssd}/neondb?sslmode=require&channel_binding=require'

engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# type alias for dependency injection
SessionDep = Annotated[Session, Depends(get_session)]
