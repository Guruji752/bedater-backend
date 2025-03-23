from app.models.debate.ParticipantsTypeMaster import ParticipantsTypeMaster
from app.schemas.participant.participant_input_schema import ParticipantInputSchema,DebateParticipantsMasterInputSchema
from app.models.debate.DebateParticipantMaster import DebateParticipantMaster
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status
from app.models.debate.DebateParticipantDetail import DebateParticipantDetail
from app.models.debate.DebateTrackerMaster import DebateTrackerMaster
from app.utils.common import get_room_id_of_debate
class ParticipantsService:

	@staticmethod
	async def create_participants_service(data,db,user):
		try:			
			user_id = user.id
			is_exist = await ParticipantsService.check_if_user_already_joined(user_id,db)
			if is_exist['status']:
				return {"msg":is_exist["msg"],"status":True}

			data_dict = data.dict()
			joined_team = data_dict['joined_team']
			debate_id = data_dict['debate_id']
			data_dict['user_id'] = user_id
			data_dict['is_locked']=True
			debate_participant_inputs = DebateParticipantsMasterInputSchema(**data_dict)
			participant_data = DebateParticipantMaster(**debate_participant_inputs.dict())
			db.add(participant_data)
			db.flush()
			participant_id = participant_data.id
			participant_type = db.query(ParticipantsTypeMaster).filter(ParticipantsTypeMaster.id == data_dict['participant_type_id']).first()
			#### Check if user joined as participant ###
			if participant_data.participant_type.participant_type == 'DEBATER':
				participant_details = {"participant_id":participant_id,"joined_team":joined_team,"debate_id":debate_id}
				return await ParticipantsService.create_participant_details(participant_details,db)
			db.commit()
			db.refresh(participant_data)
			return {"msg":"User has joined successfully as Mediator!","status":True}
		except Exception as e:
			raise HTTPException(
				status_code = status.HTTP_400_BAD_REQUEST,
				detail=f"{e}"
			)



	@staticmethod
	async def create_participant_details(data,db):
		try:
			participant_details = DebateParticipantDetail(**data)
			db.add(participant_details)
			db.commit()
			db.refresh(participant_details)
			return {"msg":"User has joined successfully as Debater!","status":200}
		except Exception as e:
			raise HTTPException(
				status_code = status.HTTP_400_BAD_REQUEST,
				detail=f"{e}"
			)

	@staticmethod
	async def check_if_user_already_joined(user_id,db):
		try:
			if_exist = db.query(DebateParticipantMaster).filter(DebateParticipantMaster.user_id == user_id,DebateParticipantMaster.is_locked==True,DebateParticipantMaster.is_active == True).first()
			if if_exist:
				return {"msg":"User is already part of debate","status":True}
			return {"status":False}
		except Exception as e:
			raise HTTPException(
				status_code = status.HTTP_400_BAD_REQUEST,
				detail=f"{e}"
			)

	@staticmethod
	async def check_participant_type(debate_id,user_id,db):
		try:
	    	### Not check through VIRTUAL ID Because while joining by the mediator virtual id won't be created ####
			participantMaster = db.query(DebateParticipantMaster).filter(DebateParticipantMaster.is_active == True,DebateParticipantMaster.debate_id == debate_id,DebateParticipantMaster.user_id == user_id).first()
			participantType = participantMaster.participant_type.participant_type
			return participantType
		except Exception as e:
			raise e


	@staticmethod
	async def update_mediator_virtual_id(virtual_id,debate_id,user_id,db):
		try:
			mediator = db.query(DebateParticipantMaster).filter(DebateParticipantMaster.is_active == True,DebateParticipantMaster.debate_id == debate_id,DebateParticipantMaster.user_id == user_id).first()
			tracker_id = db.query(DebateTrackerMaster).filter(DebateTrackerMaster.virtual_id == virtual_id).first()
			mediator.virtual_id = tracker_id.id
			db.commit()
			db.refresh(mediator)
			return {"status":True}
		except Exception as e:
			raise e

	@staticmethod
	async def isParticipantLocked(user_id,db):
		try:
			participantDetails = db.query(DebateParticipantMaster).filter(DebateParticipantMaster.user_id == user_id,DebateParticipantMaster.is_active == True).first()
			is_locked = participantDetails.is_locked
			room_id,debate_id=None,None
			if is_locked:
				debate_id = participantDetails.debate_id
				room_id = get_room_id_of_debate(debate_id,db)
			return {"is_locked":is_locked,"debate_id":debate_id,"room_id":room_id}
		except Exception as e:
			raise e

