from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
from sqlmodel import select, SQLModel, Field
from database import SessionDep
from .user_manager import User, get_current_user, oauth2_scheme
from sqlalchemy import UniqueConstraint, delete
from sqlalchemy import or_

router = APIRouter()

class WorkspaceBase(SQLModel):
    name: str = Field(index = True)
    owner: str = Field(index=True)
    
class Workspace(WorkspaceBase,table=True):
    __table_args__ = (UniqueConstraint("name", "owner"), )
    id: int = Field(default=None,primary_key=True)

class MembersBase(SQLModel):    
    workspace_id: int = Field(index=True)
    member: str

class Members(MembersBase, table=True):    
    __table_args__ = (UniqueConstraint("workspace_id", "member"), )
    id : int = Field(default=None, primary_key=True)

@router.post("/")
def create_workspace(workspace: WorkspaceBase, session: SessionDep):
    user =  session.exec(select(User).where(User.name == workspace.owner)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    workspace_db = Workspace.model_validate(workspace)
    session.add(workspace_db)
    session.commit()
    session.refresh(workspace_db)
    return workspace_db.id

@router.post("/{workspace_id}/members")
def create_member(mem: MembersBase, session: SessionDep, token: Annotated[str, Depends(oauth2_scheme)]):
    user =  session.exec(select(User).where(User.name == mem.member)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    current_user = get_current_user(session,token)
    owner = session.get(Workspace,mem.workspace_id)
    
    if owner is None:
        raise HTTPException(status_code=403, detail="Invalid  owner.")

    if owner.owner == current_user.name:
        member_class = Members.model_validate(mem)
        session.add(member_class)
        session.commit()
        session.refresh(member_class)
        return member_class
    else:
        raise HTTPException(status_code=403, detail="Invalid Owner")
    

@router.get("/")
def get_workspace(session: SessionDep, token: Annotated[str, Depends(oauth2_scheme)]):
    current_user = get_current_user(session,token)
    workspaces = []
    stmt = (
        select(Workspace.id)
        .join(Members, Workspace.id == Members.workspace_id, isouter=True)
        .filter(or_(Workspace.owner == current_user.name, Members.member == current_user.name))
    )
    accessible_ws_ids = list(session.exec(stmt))
    for k in accessible_ws_ids:
       stmt = (
           select(Workspace,Members)
           .join(Members, Workspace.id == Members.workspace_id, isouter=True)
           .where(Workspace.id == k))
       workspaces += list(session.exec(stmt).all())
    if workspaces is None:
        raise HTTPException(status_code=404, detail="No Workspace")

    result = {}
     
    for workspace, member in workspaces:
        if workspace.id not in result:
            result[workspace.id] = {
                "workspace_id": workspace.id,
                "name": workspace.name,
                "owner": workspace.owner,
                "members": []
            }
            
        if member is not None:
             result[workspace.id]["members"].append(member.member)
        else:
            if not result[workspace.id]["members"]:
                 result[workspace.id]["members"].append(" ")

    return result

@router.delete("/{workspace_id}")
def delete_workspace(workspace_id: int, token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep):
    current_user = get_current_user(session,token)
    workspace = session.get(Workspace, workspace_id)
    if not workspace:
        return None
    if workspace.owner == current_user.name:
        session.delete(workspace)
        stmt = delete(Members).where(Members.workspace_id == workspace_id)
        session.exec(stmt)
        session.commit()
        return {200 : "Deleted successfully."}
    else:
        raise HTTPException(status_code=403, detail="Invalid Owner")
    
@router.delete("/{workspace_id}/members/{membername}")
def delete_mem(workspace_id:int ,membername:str ,token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep):
    current_user = get_current_user(session,token)
    member = session.exec(select(Members).where(Members.workspace_id==workspace_id).where(Members.member==membername))
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    owner = session.get(Workspace,workspace_id)
    if owner is None:
        raise HTTPException(status_code=403, detail="Invalid  owner.")
    if owner.owner == current_user.name:    
        stmt = delete(Members).where(Members.workspace_id == workspace_id).where(Members.member == membername)
        session.exec(stmt)
        session.commit()
        return {200 : "Deleted successfully."}
    else:
        raise HTTPException(status_code=403, detail="Invalid Owner")
