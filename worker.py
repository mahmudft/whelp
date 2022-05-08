import ipaddress
import json
import os
from pprint import pprint
import time
from celery import Celery
from ipdata import ipdata
from models import *

IPDATA_KEY = os.environ.get("IPDATA_KEY", "2c6d18fcc791d52a4bcd45ea7f7bbdd88096b9998666edee36518564")

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get(
    "CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get(
    "CELERY_RESULT_BACKEND", "redis://localhost:6379")


@celery.task(name="get geolocation data")
def get_ip_data(userID, ipadress):
    ipdata = ipdata.IPData(IPDATA_KEY)
    response = ipdata.lookup(ipadress)
    task = Task.get(Task.user_id==userID,Task.ip_data==ipadress)
    task.json_result = json.encoder(response)
    task.save()
    
      # time.sleep(int(task_type) * 10)
    return response
