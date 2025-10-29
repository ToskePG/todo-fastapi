from pydantic import BaseModel, constr, EmailStr

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: constr(min_length=6, max_length=72)  # type: ignore # bcrypt-safe
    is_confirmed: bool

class UserRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    email: str

    class Config:
        from_attributes = True

class RegisterUser(BaseModel):
    first_name: str
    last_name: str
    username: constr(min_length=3, max_length=50)# type: ignore # bcrypt-safe
    email: EmailStr
    password: constr(min_length=6)# type: ignore # bcrypt-safe

class LoginUser(BaseModel):
    email: EmailStr
    password: str