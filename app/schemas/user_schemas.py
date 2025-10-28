from pydantic import BaseModel

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str

class UserRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    email: str

    class Config:
        from_attributes = True