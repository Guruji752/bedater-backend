from app.models.debate.DebateParticipantMaster import DebateParticipantMaster
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.debate.DebateTrackerMaster import DebateTrackerMaster
from app.models.debate.DebateMaster import DebateMaster
import uuid
import time
from fastapi.encoders import jsonable_encoder

from app.utils.enums import ParticipantsType,TeamSides,DebateType
from app.services.RedisServices import RedisServices
from app.models.debate.ParticipantsTypeMaster import ParticipantsTypeMaster
class ControllerServices:

	@staticmethod
	async def lock_participants_service(data,user,db):
		try:
			data_dict = data.dict()
			user_id = user.id
			debate_id = data_dict['debate_id']
			participant_type_id = data_dict['participant_type_id']

			data = db.query(DebateParticipantMaster).filter(DebateParticipantMaster.debate_id == debate_id,DebateParticipantMaster.participant_type_id == participant_type_id,DebateParticipantMaster.user_id == user_id).first()
			data.is_locked = True
			db.commit()
			return {"msg":"Partcipiant has been locked!","status":200}
		except Exception as e:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail=f"{e}"
			)
	

	@staticmethod
	async def create_debate_start(room_id,db):
		try:
			debate = db.query(DebateMaster).filter(DebateMaster.room_id == room_id).first()
			debate_id = debate.id
			if_exist = db.query(DebateTrackerMaster).filter(DebateTrackerMaster.debate_id == debate_id,DebateTrackerMaster.is_active==True).first()
			if if_exist:
				return {"msg":"Debate is already running","status":True,"virtual_id":if_exist.virtual_id,"debate_id":if_exist.debate_id}
			virtual_id = str(uuid.uuid4())
			started_at = int(time.time())
			data = {"debate_id":debate_id,"virtual_id":virtual_id,"started_at":started_at}
			debate = DebateTrackerMaster(**data)
			db.add(debate)
			db.commit()
			db.refresh(debate)
			return {"msg":"Debate start has beed create","status":True,"virtual_id":virtual_id,"debate_id":debate_id}
		except Exception as e:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail=f"{e}"
			)
	@staticmethod
	async def checkDebateStart(data,db):
		try:
			data_dict = data.dict()
			code = data_dict["code"]
			debate_master_details = db.query(DebateMaster).filter(DebateMaster.participants_code == code,DebateMaster.is_active == True).first()
			userType = ParticipantsType.DEBATER.value
			if not debate_master_details:
				userType = ParticipantsType.AUDIENCE.value
				debate_master_details = db.query(DebateMaster).filter(DebateMaster.audience_code == code,DebateMaster.is_active == True).first()
				if not debate_master_details:
					return{"msg":"No Debate Found!!","status":False}
			debate_id = debate_master_details.id
			room_id = debate_master_details.room_id
			virtual_id = db.query(DebateTrackerMaster.virtual_id).filter(DebateTrackerMaster.debate_id == debate_id,DebateTrackerMaster.is_active == True).first()
			if not virtual_id:
				return {"status":False,"msg":"You'll be allowed once debate will be start","virtual_id":None,"userTypeDetails":None}
			### checking if virtual id has been set in redis or not #### 
			# import pdb;pdb.set_trace()
			virtual_id = virtual_id[0]
			participantsTypeMaster = db.query(ParticipantsTypeMaster).filter(ParticipantsTypeMaster.participant_type == userType,ParticipantsTypeMaster.is_active == True).first()
			userTypeDetails = {"participant_type":participantsTypeMaster.participant_type,"participant_type_id":participantsTypeMaster.id}
			status,msg = await RedisServices.checkDebateStart(virtual_id)
			return {"status":status,"msg":msg,"virtual_id":virtual_id,"userTypeDetails":userTypeDetails}
		except Exception as e:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail=f"{e}"
			)

