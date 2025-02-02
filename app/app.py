from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.settings.config import settings
from app.api_v1.routers import approuter
from app.websockets.sockets import sio
import socketio
import redis

# memorydb_endpoint = "clustercfg.bedatedebatedev.pc4fe8.memorydb.us-east-2.amazonaws.com"
# redis_port = 6379


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(approuter, prefix=settings.API_V1_STR)
app.mount("/socket.io", socketio.ASGIApp(sio, app))
