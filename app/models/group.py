from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.core.database import Base

# 🔹 Pomoćna tabela za relaciju many-to-many između korisnika i grupa
group_members = Table(
    "group_members",
    Base.metadata,
    Column("group_id", ForeignKey("groups.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)

# Main table
class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    admin_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    #Relationship definition
    admin = relationship("User", backref="admin_of_group", foreign_keys=[admin_id])
    members = relationship(
        "User",
        secondary=group_members,
        back_populates="groups"
    )