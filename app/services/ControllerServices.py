from app.models.debate.DebateParticipantMaster import DebateParticipantMaster
from fastapi import APIRouter, Depends, HTTPException, status

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
	
