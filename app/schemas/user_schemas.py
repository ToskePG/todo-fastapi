from pydantic import BaseModel, constr

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: constr(min_length=6, max_length=72)  # type: ignore # bcrypt-safe

class UserRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    email: str

    class Config:
        from_attributes = True