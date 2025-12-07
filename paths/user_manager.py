from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import select, SQLModel, Field
from typing import Annotated
from database import SessionDep
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserBase(SQLModel):
    name: str = Field(index = True)
    password: str
    
class User(UserBase,table=True):
    id: int = Field(default=None,primary_key=True)
    
class UserPublic(SQLModel):
    name: str
    id: int

SECRET_KEY = "dbb5fa7441754642df2fb15632614e64df3a67e734d14ea9feedbcc79946d969" # random hex for token verification
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# to_encode = {"user_name": "test", "exp": "days"}
def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt  
        
def get_current_user(session: SessionDep, token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("user_name")
        if username is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user =  session.exec(select(User).where(User.name == username)).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/register/", response_model=UserPublic)
def create_user(user: UserBase, session: SessionDep):
    if len(user.password)<5:
        raise HTTPException(status_code=400, detail="Password too short")
    user_exist = session.exec(select(User).where(User.name == user.name)).first()
    if user_exist:
        raise HTTPException(status_code=400, detail="Username already exists")

    user.password=pwd_context.hash(user.password)
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.post("/login/")
def read_user(user: UserBase, session: SessionDep):
    user_exist = session.exec(select(User).where(User.name == user.name)).first()
    if not user_exist or not pwd_context.verify(user.password, user_exist.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    # create token    
    expiry = datetime.now(timezone.utc) + timedelta(days=180)
    expiry_timestamp = int(expiry.timestamp())  # numeric timestamp
    token = create_access_token({"user_name":user_exist.name,"exp":expiry_timestamp})
    return {"access_token": token, "token_type": "bearer"}
        
@router.get("/verify",response_model=UserPublic)
def verify_user(session: SessionDep, token: Annotated[str, Depends(oauth2_scheme)]):
    user = get_current_user(session, token)
    return user