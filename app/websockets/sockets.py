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
from app.api_v1.deps.user_deps import get_current_user
from app.models.auth.UserMaster import UserMaster
from app.services.ControllerServices import ControllerServices
from app.services.RedisServices import RedisServices
from app.services.ParticipantsServices import ParticipantsService
from app.services.ParticipantsTeamsServices import ParticipantsTeamsServices

sio = socketio.AsyncServer(cors_allowed_origins="*",async_mode='asgi')
active_users = {}

async def authenticate_user(token: str, db: Session):
    try:
        user = await get_current_user(request=None, token=token, db=db)
        return user
    except HTTPException:
        return None


@sio.event
async def connect(sid, environ):
    '''
        This connect must be fired only after user is locked for debate
    '''
    db=SessionLocal()
    try:
        query_string = environ.get("asgi.scope", {}).get("query_string", b"").decode()
        query_params = {key: value for key, value in [param.split("=") for param in query_string.split("&")]}
        
        token = query_params.get("token")
        room_id = query_params.get("room_id")
        if not token:
            await sio.disconnect(sid)
            return {"msg":"No token exist"}
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
        startDebate = await ControllerServices.create_debate_start(room_id,db)
        if startDebate['status']:
            virtual_id,debate_id = startDebate['virtual_id'],startDebate['debate_id']

        ######## Setup Redis Payload #####
            ###### check the user type ###
            userType = await ParticipantsService.check_participant_type(debate_id,user.id,db)
            if userType == "MEDIATOR":
                output = await ParticipantsService.update_mediator_virtual_id(virtual_id,debate_id,user.id,db)
                if not output["status"]:
                    raise HTTPException("Something Went Wrong! While setting up mediator virtual id")
                ####### set team details###
                await ParticipantsTeamsServices.create_participant_team_details(debate_id,virtual_id,user.id,db)
                #######################
                msg,status,data = await RedisServices.set_debate(virtual_id,user.id,debate_id,db)
            if userType == "DEBATER":
                msg,status = await RedisServices.set_or_update_debate_virtual_id(virtual_id,user.id,debate_id,db)

            #############################

        ####################################

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
async def set_debate_timer_and_status(sid,data):
    '''
            This function set time when debate starts
            and set status to True for the first time 
            and change the status on every pause/play button
    '''
    try:
        db=SessionLocal()
        user = active_users.get(sid)
        if not user:
            await sio.emit("error", {"message": "Unauthorized"})
            return
        user_details = user.get('user')
        room_id = user.get("room_id")
        if not room_id:
            await sio.emit("error", {"message": "Room ID not found"})
            return
       

        debateTimerAndStatus = await RedisServices.setDebateTimerAndStatusDetails(virtual_id,db)
        if debateTimerAndStatus["status"]:
            current_status = debateTimerAndStatus["current_status"]
            await sio.emit("debate_start_time", {"current_status": current_status}, room=room_id)


    finally:
        print("DB connection closed")
        db.close()

@sio.event
async def current_debate_remaining_time(sid,data):
    '''
        This function fetchs the current
        debate time by subtracting the time 
        from count_down_start key of redis.
    '''
    try:
        db=SessionLocal()
        user = active_users.get(sid)
        if not user:
            await sio.emit("error", {"message": "Unauthorized"})
            return {"msg":"No user found"}
        room_id = data.get("room_id")
        if not room_id:
            await sio.emit("error", {"message": "Room ID not found"})
            return {"msg":"No room found"}
        startDebate = await ControllerServices.create_debate_start(room_id,db)
        if startDebate['status']:
            virtual_id,debate_id = startDebate['virtual_id'],startDebate['debate_id']          
            curreDebateRemainigEpochDiff = await RedisServices.currentDebateRemaingTime(virtual_id,db)
            current_debate_time = curreDebateRemainigEpochDiff["epoch_diff"]
            await sio.emit("debate_start_time",{"current_debate_time":current_debate_time}, room=room_id)
    finally:
        print("DB closed")
        db.close()



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



# @sio.event
# async def timer_control(sid, data):
#     user = active_users.get(sid)
#     if not user:
#         await sio.emit("error", {"message": "Unauthorized"})
#         return

#     if not data.get("action") in ["start", "pause"]:
#         await sio.emit("error", {"message": "Invalid action"})
#         return

#     action = data["action"]
#     print(f"User {user.username} {action}ed the timer in room {data['room_id']}")
#     await sio.emit("timer_status", {"action": action}, room=data["room_id"])



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
