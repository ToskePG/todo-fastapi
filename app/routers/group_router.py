from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models.group import Group, group_members
from app.models.user import User
from app.schemas.group_schemas import GroupCreate, GroupRead, GroupUpdate, UserInGroup
from app.core.database import get_db
from app.auth.security import get_current_user

router = APIRouter(prefix="/groups", tags=["groups"])

# ----------------------
# CREATE GROUP
# ----------------------
@router.post("/", response_model=GroupRead, status_code=status.HTTP_201_CREATED)
def create_group(group_data: GroupCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_group = Group(name=group_data.name, admin_id=current_user.id)
    new_group.members.append(current_user)  # creator automatically a member
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return new_group

# ----------------------
# GET ALL GROUPS FOR USER
# ----------------------
@router.get("/", response_model=List[GroupRead], status_code=status.HTTP_200_OK)
def get_user_groups(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return current_user.groups

# ----------------------
# UPDATE GROUP (only admin)
# ----------------------
@router.put("/{group_id}", response_model=GroupRead)
def update_group(group_id: int, group_data: GroupUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if group.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only admin can update the group")
    
    if group_data.name:
        group.name = group_data.name

    db.commit()
    db.refresh(group)
    return group

# ----------------------
# ADD MEMBER (only admin)
# ----------------------
@router.post("/{group_id}/add-member/{user_id}", response_model=GroupRead)
def add_member(group_id: int, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if group.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only admin can add members")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user in group.members:
        raise HTTPException(status_code=400, detail="User already in group")

    group.members.append(user)
    db.commit()
    db.refresh(group)
    return group

# ----------------------
# REMOVE MEMBER (only admin)
# ----------------------
@router.delete("/{group_id}/remove-member/{user_id}", response_model=GroupRead)
def remove_member(group_id: int, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if group.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only admin can remove members")

    user = db.query(User).filter(User.id == user_id).first()
    if not user or user not in group.members:
        raise HTTPException(status_code=404, detail="User not in group")

    if user.id == group.admin_id:
        raise HTTPException(status_code=400, detail="Admin cannot be removed")

    group.members.remove(user)
    db.commit()
    db.refresh(group)
    return group
