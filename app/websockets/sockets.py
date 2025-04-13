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
from app.utils.common import string_to_bool
import uuid
from app.services.MediatorServices import MediatorServices
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
        virtual_id = query_params.get("virtual_id")
        is_audience = query_params.get("is_audience") ### Boolena Type
        is_audience = string_to_bool(is_audience)
        debateRoom = f"{room_id}"

        ######## audience #######
        if is_audience:
            if not (room_id):
                await sio.disconnect(sid)
                return None
            user=uuid.uuid4()
            active_users[sid] = {"user": user, "debateRoom": debateRoom,"is_audience":is_audience}
            print(active_users,"active_users")
            await sio.enter_room(sid, debateRoom)
            await sio.emit("connected", {"message": f"Welcome Guest to the debate!"}, room=debateRoom)
            print(f"Guest {user} joined in audience!! in room {debateRoom}")
            ##### Updating Audience Viwer Count ####
            await RedisServices.update_audience_count(virtual_id=virtual_id,join=True)  
            #############
            return {"msg":"Audience Member joined"}

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
        active_users[sid] = {"user": user, "debateRoom": debateRoom,"is_audience":is_audience}
        print(f"User {user.username} connected with SID {sid} and joined room {debateRoom}")
        await sio.enter_room(sid, debateRoom)
        #### Setting up time when debate first starts #####
        startDebate = await ControllerServices.create_debate_start(room_id,db)
        if startDebate['status']:
            virtual_id,debate_id = startDebate['virtual_id'],startDebate['debate_id']
            active_users[sid]["debate_id"] = debate_id
            active_users[sid]["virtual_id"] = virtual_id
        ########
        ######## Setup Redis Payload #####
            ###### check the user type ###
            userType = await ParticipantsService.check_participant_type(debate_id,user.id,db)
            if userType == "MEDIATOR":
                output = await ParticipantsService.update_mediator_virtual_id(virtual_id,debate_id,user.id,db)
                if not output["status"]:
                    raise HTTPException("Something Went Wrong! While setting up mediator virtual id")
                ####### set team details###
                await ParticipantsTeamsServices.create_participant_team_details(debate_id,virtual_id,user.id,db)

                await sio.emit("message_received", {"message": f"Welcome {user.username} to the debate! joined as mediator"}, room=debateRoom)

                #######################
                msg,status,data = await RedisServices.set_debate(virtual_id,user.id,debate_id,db)
            if userType == "DEBATER":
                team_id,team_name = await ParticipantsService.get_joined_team_details(user.id,virtual_id,db)

                msg,status = await RedisServices.set_or_update_debate_virtual_id(virtual_id,user.id,debate_id,db)
                output = await RedisServices.get_participant_avatar(team_name,virtual_id,db)
                #### fetch and store joined team id and name ###
                active_users[sid]["team_name"]=team_name
                active_users[sid]["team_id"]=team_id
                await sio.emit("message_received", {"message": output}, room=debateRoom)

            #############################

        ####################################

    finally:
        print("DB Session closed")
        db.close()

@sio.event
async def send_message(sid, data):
    user = active_users.get(sid)
    print(data,"data send data")
    if not user:
        await sio.emit("error", {"message": "Unauthorized"})
        return {"msg":"User Not Exisr"}

    user_details = user.get('user')
    debateRoom = user.get("debateRoom")
    if not debateRoom:
        await sio.emit("error", {"message": "Room ID not found"})
        return {"msg":"Can't find user id"}

    print(f"User {user_details} sent message: {data['message']} in room {debateRoom}")
    await sio.emit("message_received", {"message": data["message"]}, room=debateRoom)

@sio.event
async def get_debate_time(sid,data):
    # import pdb;pdb.set_trace()
    try:
        db=SessionLocal()
        user = active_users.get(sid)
        is_pause = data.get("is_pause")
        is_refresh = data.get("is_refresh")
        if not user:
            await sio.emit("error", {"message": "Unauthorized"})
            return
        user_details = user.get('user')
        is_audience = user.get('is_audience')
        virtual_id = user.get("virtual_id")
        debateRoom = user.get("debateRoom")
        debate_id = user.get("debate_id")
        if user and (not is_audience):
            userType = await ParticipantsService.check_participant_type(debate_id,user_details.id,db)
            if userType == "MEDIATOR":
                hour,minute,second = await MediatorServices.mediatorDebateTimer(debate_id,virtual_id,is_pause,is_refresh,db)
            await sio.emit("mediator_debate_time", {"timer":{"hour":hour,"minute":minute,"second":second},"status":True}, room=debateRoom)
            return None
        await sio.emit("mediator_debate_time",{"timer":{},"status":False})
    except Exception as e:
        raise e
    finally:
        print("DB connection closed")
        db.close()


@sio.event
async def get_participant_mediator_screen_timer(sid,data):
    try:
        db=SessionLocal()
        user = active_users.get(sid)
        topic_id = data.get('topic_id')
        topic_name = data.get('topic_name')
        virtual_id = user.get("virtual_id")
        debateRoom = user.get("debateRoom")
        debate_id = user.get("debate_id")
        hour,minute,second,teams_name = await ParticipantsService.get_team_debate_times(virtual_id,debate_id,topic_id,topic_name,db)
        await sio.emit("get_participant_mediator_screen_timer_receiver",{"timer":{"hour":hour,"minute":minute,"second":second},"team_name":teams_name,"status":True},room=debateRoom)
    except Exception as e:
        raise e
    finally:
        print("DB connection closed")
        db.close()



@sio.event
async def set_debate_timer_and_status(sid,data):
    '''
            This function set time when debate starts
            and set status to True for the first time 
            and change the status on every pause/play button
    '''
    try:
        db=SessionLocal()
        is_pause=data.get("is_pause")
        user = active_users.get(sid)
        user_details = user.get('user')
        is_audience = user.get('is_audience')
        virtual_id = user.get("virtual_id")
        debateRoom = user.get("debateRoom")
        debate_id = user.get("debate_id")
        if not user:
            await sio.emit("error", {"message": "Unauthorized"})
            return
        # user_details = user.get('user')
        # virtual_id = user.get('virtual_id')
        # room_id = user.get("room_id")
        # if not room_id:
        #     await sio.emit("error", {"message": "Room ID not found"})
        #     return
       

        debateTimerAndStatus = await RedisServices.setDebateTimerAndStatusDetails(virtual_id,is_pause,db)
        if debateTimerAndStatus["status"]:
            current_status = debateTimerAndStatus["is_pause"]
            await sio.emit("debate_start_time", {"current_status": current_status}, room=debateRoom)


    finally:
        print("DB connection closed")
        db.close()


@sio.event
async def set_team_last_pause_and_current_status(sid,data):
    '''
    This Function will be use to set the last pause time 
    of particular team and current status of topic

    current status of topic would be : 'is_pause:True/False'
    complete status:'is_complete:False/True' by default:False
    '''
    '''
    args: is_pause:(default False),is_refresh:(default False)
    '''
    db=SessionLocal()
    user = active_users.get(sid)
    user_details = user.get('user')

    is_pause = data.get("is_pause")
    user_details = user.get('user')
    virtual_id = user.get("virtual_id")
    debateRoom = user.get("debateRoom")
    debate_id = user.get("debate_id")
    if not user:
        await sio.emit("error", {"message": "Unauthorized"})
        return


    
    







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


@sio.event()
async def disconnect_participant(sid,data):
    is_referesh = data.get("is_referesh")
    print("==called==")
    if not is_referesh:
        print("inside refresh")
        db=SessionLocal()
        user = active_users.pop(sid, None)
        user_details = user.get('user')
        is_audience = user.get('is_audience')
        virtual_id = user.get("virtual_id")
        debateRoom = user.get("debateRoom")
        if user and is_audience:
            await RedisServices.update_audience_count(virtual_id=virtual_id,join=False)
            print(f"User {user_details} disconnected from room.")
        if user and (not is_audience):
            debate_id = user.get("debate_id")
            userType = await ParticipantsService.check_participant_type(debate_id,user_details.id,db)
            if userType == "DEBATER":
                team_name = user.get("team_name")
                team_id = user.get("team_id")
                await RedisServices.removeParticipantFromDebate(user_details.id,virtual_id,db)
                output = await RedisServices.get_participant_avatar(team_name,virtual_id,db)
                await sio.emit("message_received", {"message": output}, room=debateRoom)




@sio.event
async def disconnect(sid):
    user = active_users.pop(sid, None)
    return
    # db=SessionLocal()
    # user = active_users.pop(sid, None)
    # print(user,"===user===",sid,"====sid===")
    # user_details = user.get('user')
    # is_audience = user.get('is_audience')
    # virtual_id = user.get("virtual_id")
    # debateRoom = user.get("debateRoom")
    # if user and is_audience:
    #     await RedisServices.update_audience_count(virtual_id=virtual_id,join=False)
    #     print(f"User {user_details} disconnected from room.")
    # if user and (not is_audience):
    #     debate_id = user.get("debate_id")
    #     userType = await ParticipantsService.check_participant_type(debate_id,user_details.id,db)
    #     if userType == "DEBATER":
    #         team_name = user.get("team_name")
    #         team_id = user.get("team_id")
    #         await RedisServices.removeParticipantFromDebate(user_details.id,virtual_id,db)
    #         output = await RedisServices.get_participant_avatar(team_name,virtual_id,db)
    #         await sio.emit("message_received", {"message": output}, room=debateRoom)





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
