from peewee import *
from pydantic import BaseModel




class Settings(BaseModel):
    authjwt_secret_key: str = '3cH.CZqc+F!f/CKJ&k.&[A%].zk35Ba*q]?5v6{_JA?xAGg_4@.{G3q(--ZU%m/QX:7ZxP#rEv&TXm6_,jv:q&X8%&'

class User(Model):
    id = AutoField()
    username = CharField()
    email = CharField()
    password = CharField()
    created_at = DateTimeField()


class Task(Model):
    id = AutoField()
    user_id = CharField()
    ip_data = CharField()
    task_id = CharField()
    json_result = TextField()
    status = CharField()
