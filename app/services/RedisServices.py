from app.api_v1.deps.redis import get_redis_connection
from app.utils.enums import ParticipantsType
from fastapi import HTTPException, status
import json
import time
from app.models.debate.DebateParticipantTeamsDetailsMaster import DebateParticipantTeamsDetailsMaster
from app.models.debate.DebateParticipantMaster import DebateParticipantMaster
from app.models.debate.DebateParticipantDetail import DebateParticipantDetail
class RedisServices:

	@staticmethod
	async def checkDebateStart(virtual_id):
		try:
			redis = await get_redis_connection()
			exists = await redis.exists(virtual_id)
			status,msg = (False,"Debate Not started Yet") if not exists else (True,"Debate Started By Mediator")
			return status,msg
		except Exception as e:
			raise HTTPException(
				status_code = status.HTTP_400_BAD_REQUEST,
				detail=f"{e}"
			)

	@staticmethod
	async def set_debate(virtual_id,user_id,debate_id,db):
		try:
			redis = await get_redis_connection()
			exists = await redis.exists(virtual_id)
			if not exists:
				######### Fetch auto generate team name ########
				teams = db.query(DebateParticipantTeamsDetailsMaster.team_name).filter(DebateParticipantTeamsDetailsMaster.debate_id == debate_id,DebateParticipantTeamsDetailsMaster.is_active==True).all() 
				team_1,team_2 = [i[0] for i in teams]
				default_data = {f"{virtual_id}":{"count_down_start":0,"is_debate_running":True,"selected_topic":"","completed_topic":[],"total_viewer":0,"winner_team":"","is_mediator_joined":True}}
				default_data[f"{virtual_id}"][team_1]={"participants_count":0,"user_ids":[],"counter_used":0,"vote":{}}
				default_data[f"{virtual_id}"][team_2]={"participants_count":0,"user_ids":[],"counter_used":0,"vote":{}}
				await redis.set(virtual_id, json.dumps(default_data))
			data = await redis.get(virtual_id)
			debate_data = json.loads(data)
			return {"status":True,"msg":"Debate has been set!!!","data":debate_data}
		except Exception as e:
			raise HTTPException(
				status_code = status.HTTP_400_BAD_REQUEST,
				detail=f"{e}"
			)








	@staticmethod
	async def set_or_update_debate_virtual_id(virtual_id,user_id,debate_id,db):
		'''
			This function will be used
			to set key as room_id in redis
			and set base template

		'''
		try:

			'''
			{"<UUID>":{"count_down_start":"","team_1":{"counter_used":0,"vote":{"topic_1":{"type":"","count":""},"topic_2":{"type":"","count":""}}},"team_2":{"counter_used":0,"vote":{"topic_1":{"type":"","count":""},"topic_2":{"type":"","count":""}}},"selected_topic":"","completed_topic":"","team_1_total_participant":0,"team_2_total_participant":0,"total_viwer":0,"winner_team":""}}
			'''
			redis = await get_redis_connection()
			exists = await redis.exists(virtual_id)
			if not exists:
				######### Fetch auto generate team name ########
				teams = db.query(DebateParticipantTeamsDetailsMaster.team_name).filter(DebateParticipantTeamsDetailsMaster.debate_id == debate_id,DebateParticipantTeamsDetailsMaster.is_active==True).all() 
				team_1,team_2 = [i[0] for i in teams]
				default_data = {f"{virtual_id}":{"count_down_start":0,"is_debate_running":False,"selected_topic":"","completed_topic":[],"total_viewer":0,"winner_team":"","is_mediator_joined":False}}
				default_data[f"{virtual_id}"][team_1]={"participants_count":0,"user_ids":[],"counter_used":0,"vote":{}}
				default_data[f"{virtual_id}"][team_2]={"participants_count":0,"user_ids":[],"counter_used":0,"vote":{}}
				await redis.set(virtual_id, json.dumps(default_data))

			#Fetch existing or newly created data from redis
			data = await redis.get(virtual_id)
			debate_data = json.loads(data)


			##### Check which team is joined by the user ######
			participantMaster = db.query(DebateParticipantMaster).filter(DebateParticipantMaster.user_id==user_id,DebateParticipantMaster.debate_id == debate_id,DebateParticipantMaster.is_active==True).first()
			participantType = participantMaster.participant_type.participant_type
			if participantType == ParticipantsType.DEBATER.value:
				participantId = participantMaster.id
				debateDetails = db.query(DebateParticipantDetail).filter(DebateParticipantDetail.participant_id == participantId,DebateParticipantDetail.is_active==True).first()
				joined_team = debateDetails.debate_participant_teams_details_master.team_name

				if user_id not in debate_data[f"{virtual_id}"][joined_team]["user_ids"]:
					debate_data[f"{virtual_id}"][joined_team]["user_ids"].append(user_id)
					debate_data[f"{virtual_id}"][joined_team]["participants_count"]+=1
			if participantType == ParticipantsType.MEDIATOR.value:				
				debate_data[f"{virtual_id}"]['is_mediator_joined']=True

			if participantType == ParticipantsType.AUDIENCE.value:
				debate_data[f"{virtual_id}"]["total_viewer"]+=1
			await redis.set(virtual_id, json.dumps(debate_data))
			await redis.close()
			return {"msg":"Data has been updated Successfully!!","status":True}

		except Exception as e:
			raise HTTPException(
				status_code = status.HTTP_400_BAD_REQUEST,
				detail=f"{e}"
			)

		#######################

	@staticmethod
	async def setDebateTimerAndStatusDetails(virtual_id,db):
		'''
			This function set time when debate starts
			and set status to True for the first time 
			and change the status on every pause/play button
		'''
		redis = await get_redis_connection()
		exists = await redis.exists(virtual_id)
		current_epoch = int(time.time())
		if exists:
			data = await redis.get(virtual_id)
			debate_data = json.loads(data)

			count_down_start_value = debate_data[f"{virtual_id}"]["count_down_start"]
			if not count_down_start_value:
				debate_data[f"{virtual_id}"]["count_down_start"]=current_epoch
			current_status = debate_data[f"{virtual_id}"]["is_debate_running"]
			update_status = True if not current_status else False ### This will reverse the current status of debate
			debate_data[f"{virtual_id}"]["is_debate_running"] = update_status
			await redis.set(virtual_id, json.dumps(debate_data))
			await redis.close()
			msg = "Current Debate status is Active" if update_status else "Current Debate status is In-Active"
			return {"msg":msg,"current_status":update_status,"status":True}
		return {"msg":"Debate is not started yet","status":False}

	@staticmethod
	async def currentDebateRemaingTime(virtual_id,db):
		redis = await get_redis_connection()
		exists = await redis.exists(virtual_id)
		if exists:
			data = await redis.get(virtual_id)
			debate_data = json.loads(data)
			### check if debate is in ACTIVE state right now ####
			current_status = debate_data[f"{virtual_id}"]["is_debate_running"]
			if current_status:
				count_down_start = debate_data[f"{virtual_id}"]["count_down_start"]
				current_epoch = int(time.time())
				diff = current_epoch - count_down_start
				return {"msg":"Difference Epoch","status":True,"epoch_diff":diff}
		return {"msg":"Debate is not started yet","status":False}


			#######################





