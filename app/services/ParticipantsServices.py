from app.models.debate.ParticipantsTypeMaster import ParticipantsTypeMaster
from app.schemas.participant.participant_input_schema import ParticipantInputSchema,DebateParticipantsMasterInputSchema
from app.models.debate.DebateParticipantMaster import DebateParticipantMaster
from fastapi.encoders import jsonable_encoder
from app.models.debate.DebateParticipantDetail import DebateParticipantDetail

class ParticipantsService:

	@staticmethod
	async def create_participants_service(data,db,user):
		user_id = user.id
		data_dict = data.dict()
		joined_team = data_dict['joined_team']
		debate_id = data_dict['debate_id']
		data_dict['user_id'] = user_id
		debate_participant_inputs = DebateParticipantsMasterInputSchema(**data_dict)
		participant_data = DebateParticipantMaster(**debate_participant_inputs.dict())
		db.add(participant_data)
		db.flush()
		participant_id = participant_data.id
		participant_type = db.query(ParticipantsTypeMaster).filter(ParticipantsTypeMaster.id == data_dict['participant_type_id']).first()
		if participant_data.participant_type.participant_type == 'DEBATER':
			participant_details = {"participant_id":participant_id,"joined_team":joined_team,"debate_id":debate_id}
			return await ParticipantsService.create_participant_details(participant_details,db)
		db.commit()
		db.refresh(participant_data)
		return {"msg":"User has joined successfully as Mediator!","status":200}
		
	@staticmethod
	async def create_participant_details(data,db):
		import pdb;pdb.set_trace()
		participant_details = DebateParticipantDetail(**data)
		db.add(participant_details)
		db.commit()
		db.refresh(participant_details)
		return {"msg":"User has joined successfully as Debater!","status":200}




