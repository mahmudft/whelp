from datetime import datetime
import json
from unicodedata import name
import celery
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from peewee import *
from Interfaces import LoginInput, SignupInput, TaskInput
from models import *
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from worker import *
from celery.result import AsyncResult, ResultBase


app = FastAPI()

mysql_db = MySQLDatabase('whelp_test', user='root', password='root',
                         host=os.environ.get(
                             "MYSQL_HOST", "127.0.0.1"), port=3306)
User.bind(mysql_db)
Task.bind(mysql_db)


@AuthJWT.load_config
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.on_event("startup")
def startup():
    mysql_db.connect()
    mysql_db.create_tables([Task, User])


@app.on_event("shutdown")
def shutdown():
    if not mysql_db.is_closed():
        mysql_db.close()

@app.get("/")
async def start():
    return {"message": "Test"}


@app.post("/api/v1/login")
async def login(user: LoginInput, Authorize: AuthJWT = Depends()):
    db_user = User.get(User.email == user.email)
    if db_user.password == user.password:
        access_token = Authorize.create_access_token(subject=db_user.email)
        refresh_token = Authorize.create_refresh_token(subject=db_user.email)
        return {"access_token": access_token, "refresh_token": refresh_token}
    else:
        return {"message": "User credentials are wrong"}


@app.post("/api/v1/signup")
async def signup(input: SignupInput):
    user = User.get_or_none(User.email == input.email)
    if user is None:
        data = User(username=input.username,
                    email=input.email, password=input.password)
        data.created_at = datetime.now()
        data.save()
        return data
    else:
        return {"message": "User exsists"}


@app.post("/api/v1/refresh")
async def refresh_token(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()

    current_user = Authorize.get_jwt_subject()
    access_token = Authorize.create_access_token(subject=current_user)
    refresh_token = Authorize.create_refresh_token(subject=current_user)
    return {"access_token": access_token, "refresh_token": refresh_token}


@app.post("/api/v1/task")
async def create_task(input: TaskInput, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    user = User.get_or_none(User.email == current_user)
    checkTask = Task.get_or_none(Task.user_id == user.id,
                         Task.task_id == input.ip_adress)
    if checkTask is None:
        task = get_ip_data.delay(user.id, input.ip_adress)
        TaskDb = Task(user_id=user.id, ip_data=input.ip_adress,task_id=task.id, json_result="test")
        TaskDb.save()
        return JSONResponse({"task_id": task.id})
    else:
        return {"message": "Task already created by current user"}


@app.get("/api/v1/status/{id}")
async def get_task(id):
    task = Task.get_or_none(Task.task_id == id)
    if task is None:
        return {"message": "No task with given id"}
    else:
        result = AsyncResult(id, app=celery)
        response = {
            "task_id": result.id,
            "task_status": result.state,
            "task_result": result.result
        }
        return JSONResponse(response)


@app.get("/api/v1/user")
async def get_user(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    incoming_user = Authorize.get_jwt_subject()

    user = User.get(User.email == incoming_user)
    return {"id": user.id, "username": user.username, "email": user.email, "created_at": user.created_at}
