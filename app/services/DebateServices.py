from fastapi import APIRouter, Depends, HTTPException, status
from app.api_v1.deps.db_deps import get_transaction_session
from sqlalchemy.orm import Session
from app.schemas.debate.debate_input_schema import CreateDebateInputSchema,CreateDebateBaseInputSchema,DebateMasterInputSchema
from app.models.debate.DebateTypeMaster import DebateTypeMaster
from app.utils.enums import DebateType
from app.services.FreeStyleServices import FreeStyleServices
from app.utils.common import generate_room_id,generate_codes
from app.models.debate.DebateMaster import DebateMaster
from app.services.FreeStyleServices import FreeStyleServices
from app.services.IntermediateStyleServices import IntermediateStyleService
from app.services.AdvanceStyleServices import AdvanceStyleService
from app.services.ParticipantsTeamsServices import ParticipantsTeamsServices
from app.models.debate.DebateStatusTypeMaster import DebateStatusTypeMaster
from app.utils.enums import DebateStatus
from fastapi.encoders import jsonable_encoder
from app.models.debate.DebateSaveMaster import DebateSaveMaster



class DebateServices:

	@staticmethod
	async def create_debate_service(data:CreateDebateInputSchema,db,user):
		user_id = user.id
		data_dict = data.dict()
		common = data_dict['common_details']
		debate_type_id = common['debate_type_id']
		debate_type = db.query(DebateTypeMaster).filter(DebateTypeMaster.id == debate_type_id,DebateTypeMaster.is_active == True).first()
		room_id = generate_room_id()
		participants_code,audience_code = generate_codes()
		debate_base_details = CreateDebateBaseInputSchema(**common)
		debate_base_details_dict = debate_base_details.dict()
		debate_base_details_dict['room_id'] = room_id
		debate_base_details_dict['participants_code'] = participants_code
		debate_base_details_dict['audience_code'] = audience_code
		debate_base_details_dict['created_by'] = user_id

		debate_status_type = DebateStatus.UPCOMINGDEBATE.value
		debate_status_type = db.query(DebateStatusTypeMaster).filter(DebateStatusTypeMaster.type == debate_status_type,DebateStatusTypeMaster.is_active == True).first()
		debate_status_type_id = debate_status_type.id
		debate_base_details_dict["debate_status_type_id"] = debate_status_type_id

		debate_master_input = DebateMasterInputSchema(**debate_base_details_dict)
		debate_master = DebateMaster(**debate_master_input.dict())
		try:
			db.add(debate_master)
			db.flush()
			debate_id = debate_master.id
			data_dict['debate_id'] = debate_id
			participant_details = await ParticipantsTeamsServices.create_participant_teams_details(debate_id,user_id,db)
			if not participant_details['status']:
				raise f"Something went wrong!"
			teams_details = participant_details['data']
			if debate_type.type == DebateType.FREESTYLE.value:
				return await FreeStyleServices.create_freestyle(data_dict,user_id,db)
			if debate_type.type == DebateType.ADVANCE.value:
				return await AdvanceStyleService.create_advance(data_dict,user_id,teams_details,db)
			if debate_type.type == DebateType.INTERMEDIATE.value:
				return await IntermediateStyleService.create_intermediate(data_dict,user_id,teams_details,db)

		except Exception as e:
			raise e

	@staticmethod
	async def listDebates(debate_status_type_id,user,db):

		user_id = user.id
		list_debate = db.query(DebateMaster).filter(DebateMaster.debate_status_type_id == debate_status_type_id,DebateMaster.created_by == user_id).all()
		return jsonable_encoder(list_debate)


	@staticmethod
	async def saveDebates(debate_id,user,db):
		debate = db.query(DebateMaster).filter(DebateMaster.id == debate_id).first()
		save_debate = DebateStatus.SAVEDDEBATED.value
		user_id = user.id
		debate_status_type = db.query(DebateStatusTypeMaster).filter(DebateStatusTypeMaster.type == save_debate).first()
		debate_status_type_id = debate_status_type.id
		data = {"debate_id":debate_id,"debate_status_type_id":debate_status_type_id,"created_by":user_id}
		is_debate_saved = db.query(DebateSaveMaster).filter(DebateSaveMaster.debate_id == debate_id,DebateSaveMaster.is_active == True).first()
		if is_debate_saved:
			return {"msg":"Debate is already saved!",status:200}
		debate_save_master = DebateSaveMaster(**data)
		db.add(debate_save_master)
		db.commit()
		return {"msg":"Debate has been saved!","status":200} 





		

