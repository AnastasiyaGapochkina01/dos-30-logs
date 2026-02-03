import logging
import socket
import time
import random
import os
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

app = FastAPI(title="Fake Server Store API")

APP_NAME = "server-store-api"
HOSTNAME = socket.gethostname()

os.makedirs("logs", exist_ok=True)

class ContextFilter(logging.Filter):
    def filter(self, record):
        record.hostname = HOSTNAME
        record.app_name = APP_NAME
        return True

logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("logs/app.log")
file_handler.addFilter(ContextFilter())

formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(hostname)s %(app_name)s %(method)s %(url)s %(client_ip)s %(message)s %(duration).3f'
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.propagate = False

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: ASGIApp):
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        url = request.url.path

        start_time = time.time()

        try:
            response = await call_next(request)
            duration = (time.time() - start_time) * 1000  # в мс

            logger.info(
                f"Request processed successfully. Status: {response.status_code}",
                extra={
                    'method': method,
                    'url': url,
                    'client_ip': client_ip,
                    'duration': duration
                }
            )
            return response
        except Exception as exc:
            duration = (time.time() - start_time) * 1000

            logger.error(
                f"Request failed: {str(exc)}",
                extra={
                    'method': method,
                    'url': url,
                    'client_ip': client_ip,
                    'duration': duration
                }
            )
            raise

app.add_middleware(LoggingMiddleware)

SERVERS = [
    {"id": 1, "model": "Dell PowerEdge R750", "cpu": "2x Intel Xeon Gold", "ram_gb": 512, "price_usd": 15000},
    {"id": 2, "model": "HP ProLiant DL380", "cpu": "2x AMD EPYC", "ram_gb": 1024, "price_usd": 25000},
    {"id": 3, "model": "Supermicro SYS-4029GP-TR", "cpu": "4x Intel Xeon", "ram_gb": 2048, "price_usd": 45000},
]

@app.get("/")
async def root():
    _simulate_load()
    return {"message": "Welcome to Fake Server Store API"}

@app.get("/servers")
async def list_servers():
    _simulate_load()
    return SERVERS

@app.get("/servers/{server_id}")
async def get_server(server_id: int):
    _simulate_load()
    server = next((s for s in SERVERS if s["id"] == server_id), None)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return server

@app.post("/servers")
async def create_server():
    _simulate_load()
    return {"id": len(SERVERS) + 1, "message": "Server created successfully"}

def _simulate_load():
    """Симуляция нагрузки и ошибок"""
    if random.random() < 0.1:
        time.sleep(random.uniform(0.5, 5))
    if random.random() < 0.05:
        raise HTTPException(status_code=random.choice([400, 500, 503]),
                          detail=random.choice(["Invalid data", "DB error", "Service unavailable"]))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)