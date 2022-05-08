from pydantic import BaseModel


class SignupInput(BaseModel):
    username: str
    email: str
    password: str


class LoginInput(BaseModel):
    email: str
    password: str

class TaskInput(BaseModel):
    ip_adress: str