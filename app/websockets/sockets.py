from fastapi import FastAPI, APIRouter ,WebSocket,WebSocketDisconnect,HTTPException
from typing import Optional
from collections import defaultdict
import json
import socketio
from app.settings.config import settings
from app.api_v1.deps.user_deps import get_current_user
from app.api_v1.deps.db import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.api_v1.deps.db import SessionLocal



sio = socketio.AsyncServer(cors_allowed_origins="*",async_mode='asgi')
active_users = {}

async def authenticate_user(token: str, db: Session):
    try:
        user = await get_current_user(request=None, token=token, db=db)
        return user
    except HTTPException:
        return None

connected_clients = set()


# @sio.event
# async def connect(sid, environ):
#     try:
#         print(f"✅ User {sid} connected")
#         await sio.emit("connected", {"message": f"User {sid} joined!"}, room=sid)
#     except Exception as e:
#         print(f"❌ Error in connect: {e}")
#         await sio.disconnect(sid)

# @sio.event
# async def send_message(sid, data):
#     try:
#         print(f"📩 Received message from {sid}: {data}")
#         await sio.emit("message_received", data, skip_sid=sid)  # Send to all except sender
#     except Exception as e:
#         print(f"❌ Error in send_message: {e}")

# @sio.event
# async def disconnect(sid):
#     try:
#         print(f"❌ User {sid} disconnected")
#         connected_clients.discard(sid)
#     except Exception as e:
#         print(f"❌ Error in disconnect: {e}")

@sio.event
async def connect(sid, environ):

    db=SessionLocal()
    try:
        query_string = environ.get("asgi.scope", {}).get("query_string", b"").decode()
        query_params = {key: value for key, value in [param.split("=") for param in query_string.split("&")]}
        
        token = query_params.get("token")
        room_id = query_params.get("room_id")
        if not token:
            print("No token")
            await sio.disconnect(sid)
            return
        user = await authenticate_user(token,db)

        if not user:
            print("No user")
            await sio.disconnect(sid)
            return 
        if not room_id:
            await sio.disconnect(sid)
            return
        active_users[sid] = {"user": user, "room_id": room_id}

        print(f"User {user.username} connected with SID {sid} and joined room {room_id}")
        await sio.enter_room(sid, room_id)
        await sio.emit("connected", {"message": f"Welcome {user.username} to the debate!"}, room=room_id)
    finally:
        print("DB Session closed")
        db.close()

@sio.event
async def send_message(sid, data):
    user = active_users.get(sid)
    if not user:
        await sio.emit("error", {"message": "Unauthorized"})
        return

    user_details = user.get('user')
    room_id = user.get("room_id")
    if not room_id:
        await sio.emit("error", {"message": "Room ID not found"})
        return

    print(f"User {user_details.username} sent message: {data['message']} in room {room_id}")
    await sio.emit("message_received", {"message": data["message"]}, room=room_id)

@sio.event
async def vote(sid, data):
    user = active_users.get(sid)
    if not user:
        await sio.emit("error", {"message": "Unauthorized"})
        return

    room_id = data.get("room_id")
    vote = data.get("vote")
    if not room_id or vote not in ["agree", "disagree"]:
        await sio.emit("error", {"message": "Invalid vote"})
        return

    print(f"User {user.username} voted {vote} in room {room_id}")
    await sio.emit("vote_received", {"user": user.username, "vote": vote}, room=room_id)


@sio.event
async def timer_control(sid, data):
    user = active_users.get(sid)
    if not user:
        await sio.emit("error", {"message": "Unauthorized"})
        return

    if not data.get("action") in ["start", "pause"]:
        await sio.emit("error", {"message": "Invalid action"})
        return

    action = data["action"]
    print(f"User {user.username} {action}ed the timer in room {data['room_id']}")
    await sio.emit("timer_status", {"action": action}, room=data["room_id"])


@sio.event
async def update_topic(sid, data):
    user = active_users.get(sid)
    if not user:
        await sio.emit("error", {"message": "Unauthorized"})
        return

    room_id = data.get("room_id")
    topic = data.get("topic")
    if not room_id or not topic:
        await sio.emit("error", {"message": "Invalid topic"})
        return

    # Assume only mediator can update the topic
    if not user.is_mediator:
        await sio.emit("error", {"message": "You are not authorized to update the topic"})
        return

    print(f"Mediator {user.username} updated the topic to '{topic}' in room {room_id}")
    await sio.emit("topic_updated", {"topic": topic}, room=room_id)


@sio.event
async def disconnect(sid):
    user = active_users.pop(sid, None)
    user_details = user.get('user')
    if user:
        print(f"User {user_details.username} disconnected from room.")


@sio.event
async def disconnect_all(sid, data):
    user = active_users.get(sid)
    if not user:
        await sio.emit("error", {"message": "Unauthorized"})
        return

    room_id = data.get("room_id")
    if not room_id:
        await sio.emit("error", {"message": "Room ID not found"})
        return

    if not user.is_mediator:
        await sio.emit("error", {"message": "You are not authorized to disconnect the room."})
        return

    print(f"Mediator {user.username} is disconnecting all users from room {room_id}")
    await sio.emit("disconnected", {"message": "The mediator has ended the debate."}, room=room_id)
    
    for sid in list(sio.rooms(room_id)):
        await sio.disconnect(sid)
        print(f"Disconnected {sid} from room {room_id}")
