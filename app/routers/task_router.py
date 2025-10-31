from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models.task import Task
from app.models.user import User
from app.models.group import Group
from app.schemas.task_schemas import TaskCreate, TaskRead, TaskUpdate
from app.core.database import get_db
from app.auth.security import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

# ----------------------
# CREATE TASK
# ----------------------
@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(task_data: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if task_data.group_id:
        group = db.query(Group).filter(Group.id == task_data.group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        # Ako postoji assignee, mora biti član grupe
        if task_data.assignee_id:
            assignee = db.query(User).filter(User.id == task_data.assignee_id).first()
            if not assignee or assignee not in group.members:
                raise HTTPException(status_code=400, detail="Assignee must be a group member")
    else:
        if task_data.assignee_id:
            raise HTTPException(status_code=400, detail="Cannot assign individual task to another user")

    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        due_date=task_data.due_date,
        priority=task_data.priority,
        creator_id=current_user.id,
        assignee_id=task_data.assignee_id,
        group_id=task_data.group_id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

# ----------------------
# GET USER TASKS (pending / done)
# ----------------------
@router.get("/", response_model=List[TaskRead])
def get_my_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Task).filter(
        ((Task.assignee_id == current_user.id) | (Task.creator_id == current_user.id))
    ).all()

@router.get("/pending", response_model=List[TaskRead])
def get_pending_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Task).filter(
        ((Task.assignee_id == current_user.id) | (Task.creator_id == current_user.id)) &
        (Task.is_done == False)
    ).all()

@router.get("/done", response_model=List[TaskRead])
def get_done_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Task).filter(
        ((Task.assignee_id == current_user.id) | (Task.creator_id == current_user.id)) &
        (Task.is_done == True)
    ).all()

# ----------------------
# UPDATE TASK
# ----------------------
@router.put("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, task_data: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Samo creator ili assignee mogu update-ovati
    if task.creator_id != current_user.id and task.assignee_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update task")

    for field, value in task_data.dict(exclude_unset=True).items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task

# ----------------------
# DELETE TASK
# ----------------------
@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Samo creator može da briše task
    if task.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete task")

    db.delete(task)
    db.commit()
    return {"detail": "Task deleted successfully"}
