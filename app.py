from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
import datetime
import random
import os
import json

app = FastAPI()

LOG_DIR = "./logs"
LOG_FILE = f"{LOG_DIR}/time-app.log"
LARGE_LOG_FILE = f"{LOG_DIR}/large.log"

methods = ["GET", "POST", "PUT", "DELETE"]
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "curl/7.68.0",
    "PostmanRuntime/7.26.10",
    "HTTPie/2.4.0",
    "python-requests/2.25.1"
]


def fake_log_entry():
    now = datetime.datetime.now().isoformat()
    ip = f"{random.randint(10, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
    method = random.choice(methods)
    user_agent = random.choice(user_agents)

    log = {
        "timestamp": now,
        "ip": ip,
        "method": method,
        "user_agent": user_agent,
        "path": "/"
    }
    return json.dumps(log, ensure_ascii=False) + "\n"


@app.get("/")
async def root():
    now = datetime.datetime.now()
    return JSONResponse({
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S")
    })


@app.get("/logs")
async def logs():
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        for _ in range(5):
            f.write(fake_log_entry())
    return FileResponse(path=LOG_FILE, media_type="text/plain", filename="time-app.log")


@app.get("/longlog")
async def longlog():
    services = {
        "postgresql": [
            'connection authorized: user=admin database=main',
            'query executed: SELECT * FROM users;',
            'user logged out: user=admin',
            'backup started',
            'checkpoint complete'
        ],
        "redis": [
            'Accepted connection from 127.0.0.1:51284',
            'SET key1 value1',
            'DEL key1',
            'SAVE completed',
            'Connection closed'
        ],
        "systemd": [
            'Started Time App FastAPI Service.',
            'Reloading.',
            'Stopping Time App FastAPI Service.',
            'Session 1 of user admin started.',
            'Service restarted.'
        ],
        "docker": [
            'Container time-app started.',
            'Image pulled fastapi:latest.',
            'Container time-app stopped.',
            'Network created bridge0.',
            'Volume logs attached.'
        ]
    }

    os.makedirs(LOG_DIR, exist_ok=True)
    now = datetime.datetime.now().isoformat()

    with open(LARGE_LOG_FILE, "w", encoding="utf-8") as f:
        for service, logs in services.items():
            for message in logs:
                entry = {
                    "timestamp": now,
                    "service": service,
                    "message": message
                }
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return {"status": "logs generated"}
