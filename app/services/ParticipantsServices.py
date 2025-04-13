from app.models.debate.ParticipantsTypeMaster import ParticipantsTypeMaster
from app.schemas.participant.participant_input_schema import ParticipantInputSchema,DebateParticipantsMasterInputSchema
from app.models.debate.DebateParticipantMaster import DebateParticipantMaster
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status
from app.models.debate.DebateParticipantDetail import DebateParticipantDetail
from app.models.debate.DebateTrackerMaster import DebateTrackerMaster
from app.utils.common import get_room_id_of_debate,get_virtual_id_fk,get_debate_type,get_debate_team_name
from app.models.debate.DebateParticipantTeamsDetailsMaster import DebateParticipantTeamsDetailsMaster
from app.utils.common import get_virtual_id_fk
from app.models.debate.AdvanceDebateTopicTimeMaster import AdvanceDebateTopicTimeMaster
from app.models.debate.AdvanceDebateDetailsMaster import AdvanceDebateDetailsMaster
from app.services.RedisServices import RedisServices
class ParticipantsService:

	@staticmethod
	async def create_participants_service(data,db,user):
		try:			
			user_id = user.id
			is_exist = await ParticipantsService.check_if_user_already_joined(user_id,db)
			if is_exist['status']:
				return {"msg":is_exist["msg"],"status":True}

			data_dict = data.dict()
			virtual_id = data_dict["virtual_id"]

			if virtual_id:
				virtual_id_fk = get_virtual_id_fk(virtual_id,db)
				data_dict['virtual_id']=virtual_id_fk
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
			# import pdb;pdb.set_trace()
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
			output = {"is_locked":False,"debate_id":None,"room_id":None}
			if participantDetails:
				is_locked = participantDetails.is_locked
				room_id,debate_id=None,None
				if is_locked:
					debate_id = participantDetails.debate_id
					room_id = get_room_id_of_debate(debate_id,db)
					# virtual_id = participantDetails.virtual.virtual_id
					output["is_locked"] = is_locked
					output["debate_id"] = debate_id
					output["room_id"] = room_id
			return output
		except Exception as e:
			raise e

	@staticmethod
	async def participantType(db):
		try:
			participantType = db.query(ParticipantsTypeMaster).filter(ParticipantsTypeMaster.is_active == True).all()
			return jsonable_encoder(participantType)
		except Exception as e:
			raise e

	@staticmethod
	async def get_joined_team_details(user_id,virtual_id,db):
		virtaul_id_fk = get_virtual_id_fk(virtual_id,db)

		participantMaster = db.query(DebateParticipantMaster).filter(DebateParticipantMaster.user_id == user_id,DebateParticipantMaster.virtual_id == virtaul_id_fk,DebateParticipantMaster.is_active == True).first()
		participantDetails = db.query(DebateParticipantDetail).filter(DebateParticipantDetail.participant_id  == participantMaster.id).first()
		joinedTeam = participantDetails.joined_team
		teamDetails = db.query(DebateParticipantTeamsDetailsMaster).filter(DebateParticipantTeamsDetailsMaster.team_id == joinedTeam,DebateParticipantTeamsDetailsMaster.is_active == True).first()
		team_name = teamDetails.team_name
		team_id = teamDetails.team_id
		return team_id,team_name
	
	@staticmethod
	async def get_team_debate_times(virtual_id,debate_id,topic_id,topic_name,db):
		debate_type = get_debate_type(debate_id,db)
		# import pdb;pdb.set_trace()
		# await RedisServices.set_participant_time_details(virtual_id,debate_type,topic_id)
		if debate_type == "ADVANCE":
			hour,minute,second,teams_name = await ParticipantsService.get_advance_debate_topic_time(debate_id,topic_id,db)
			await RedisServices.set_participant_time_details(virtual_id,teams_name,debate_type,topic_name)
			return hour,minute,second,teams_name
		if debate_type == 'FREESTYLE':
			hour,minute,second,teams_name = await ParticipantsService.get_freestyle_intermediate_topic_time(debate_id,db)
			await RedisServices.set_participant_time_details(virtual_id,teams_name,debate_type,topic_name)
			return hour,minute,second,teams_name
		if debate_type == 'INTERMEDIATE':
			hour,minute,second,teams_name =  await ParticipantsService.get_freestyle_intermediate_topic_time(debate_id,db)
			await RedisServices.set_participant_time_details(virtual_id,teams_name,debate_type,topic_name)
			return hour,minute,second,teams_name
	@staticmethod
	async def get_advance_debate_topic_time(debate_id,topic_id,db):
		topicTimer = db.query(AdvanceDebateTopicTimeMaster).filter(AdvanceDebateTopicTimeMaster.debate_id == debate_id,AdvanceDebateTopicTimeMaster.topic_id == topic_id).first()
		hour,minute,second = topicTimer.hour,topicTimer.minute,topicTimer.seconds
		## Check team Side ###
		advanceDebateDetails = db.query(AdvanceDebateDetailsMaster).filter(AdvanceDebateDetailsMaster.topic_id == topicTimer.topic_id,AdvanceDebateDetailsMaster.debate_id == debate_id).first()
		team_id = advanceDebateDetails.team_id
		debateParticipantTeamDetailsMaster = db.query(DebateParticipantTeamsDetailsMaster).filter(DebateParticipantTeamsDetailsMaster.team_id == team_id,DebateParticipantTeamsDetailsMaster.debate_id == debate_id).first()
		team_name = debateParticipantTeamDetailsMaster.team_name
		return hour,minute,second,[team_name]
	@staticmethod
	async def get_freestyle_intermediate_topic_time(debate_id,db):
		return await ParticipantsService.get_debate_half_time(debate_id,db)

	@staticmethod
	async def get_debate_half_time(debate_id,db):
		debate = db.query(DebateMaster).filter(DebateMaster).filter(DebateMaster.id == debate_id,DebateMaster.is_active == True).first()
		hour,minute,second = int(debate.hour),int(debate.minute),int(debate.seconds)
		total_duration_seconds = hour * 3600 + minute * 60 + second
		half_time = total_duration_seconds//2
		hour = remaining_seconds // 3600
		remaining_seconds %= 3600
		minute = remaining_seconds // 60
		second = remaining_seconds % 60
		if hour <= 0 and minute <= 0 and second <= 0:
			hour = 0
			minute = 0
			second = 0
		teams_name = get_debate_team_name(debate_id,db)
		return hour,minute,second,teams_name










