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
# CREATE TASK IN GROUP
# ----------------------
@router.post("/group/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_group_task(group_name: str, task_data: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Pronađi grupu po imenu
    group = db.query(Group).filter(Group.name == group_name).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Assignee mora biti član grupe, ili None
    assignee_id = task_data.assignee_id
    if assignee_id:
        assignee = db.query(User).filter(User.id == assignee_id).first()
        if not assignee or assignee not in group.members:
            raise HTTPException(status_code=400, detail="Assignee must be a member of the group")
    else:
        assignee_id = None

    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        due_date=task_data.due_date,
        priority=task_data.priority,
        creator_id=current_user.id,
        assignee_id=assignee_id,
        group_id=group.id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


# ----------------------
# CREATE INDIVIDUAL TASK
# ----------------------
@router.post("/individual/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_individual_task(task_data: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Individualni task -> samo creator i assignee samom sebi
    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        due_date=task_data.due_date,
        priority=task_data.priority,
        creator_id=current_user.id,
        assignee_id=current_user.id,
        group_id=None
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


# ----------------------
# GET ALL TASKS FOR USER
# ----------------------
@router.get("/", response_model=List[TaskRead])
def get_my_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Task).filter(
        (Task.assignee_id == current_user.id) | (Task.creator_id == current_user.id)
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
