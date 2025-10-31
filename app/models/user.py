from sqlalchemy import Column, Integer, String,Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_confirmed = Column(Boolean, default=False)

    #Relationship definition
    groups = relationship(
        "Group",
        secondary="group_members",
        back_populates="members",
    )
