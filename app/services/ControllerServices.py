from app.models.debate.DebateParticipantMaster import DebateParticipantMaster
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.debate.DebateTrackerMaster import DebateTrackerMaster
from app.models.debate.DebateMaster import DebateMaster
import uuid
import time


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
