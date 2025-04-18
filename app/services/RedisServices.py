from app.api_v1.deps.redis import get_redis_connection
from app.utils.enums import ParticipantsType
from fastapi import HTTPException, status
import json
import time
from app.models.debate.DebateParticipantTeamsDetailsMaster import DebateParticipantTeamsDetailsMaster
from app.models.debate.DebateParticipantMaster import DebateParticipantMaster
from app.models.debate.DebateParticipantDetail import DebateParticipantDetail
from app.models.debate.DebateTrackerMaster import DebateTrackerMaster
from app.models.debate.DebateParticipantTeamsDetailsMaster import DebateParticipantTeamsDetailsMaster
from app.models.avatar.AvatarMaster import AvatarMaster
from app.utils.common import get_virtual_id_fk
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
				default_data = {f"{virtual_id}":{"count_down_start":0,"last_paused":0,'last_started':0,"is_debate_running":True,"selected_topic":"","completed_topic":[],"total_viewer":0,"winner_team":"","is_mediator_joined":True}}
				default_data[f"{virtual_id}"][team_1]={"participants_count":0,"user_ids":[],"counter_used":0,"vote":{},"FREESTYLE":{},"INTERMEDIATE":{},"ADVANCE":{}}
				default_data[f"{virtual_id}"][team_2]={"participants_count":0,"user_ids":[],"counter_used":0,"vote":{},"FREESTYLE":{},"INTERMEDIATE":{},"ADVANCE":{}}
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
				### check virtual id , id from tracker master ###
				virtualId = db.query(DebateTrackerMaster).filter(DebateTrackerMaster.virtual_id == virtual_id,DebateTrackerMaster.is_active	== True).first()
				virtualId = virtualId.id
				joined_team = debateDetails.joined_team
				####
				######## fetch team detail ###
				teamDetails = db.query(DebateParticipantTeamsDetailsMaster).filter(DebateParticipantTeamsDetailsMaster.virtual_id == virtualId,DebateParticipantTeamsDetailsMaster.team_id == joined_team,DebateParticipantTeamsDetailsMaster.is_active == True).first()
				joined_team = teamDetails.team_name

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
	async def setDebateTimerAndStatusDetails(virtual_id,is_pause,db):
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
				debate_data[f"{virtual_id}"]["last_paused"]=0
			if is_pause:
				last_pause=debate_data[f"{virtual_id}"]["last_paused"]
				last_started = debate_data[f"{virtual_id}"]["last_started"]
				epoch_diff = last_started - last_pause
				current_pause = current_epoch-epoch_diff
				debate_data[f"{virtual_id}"]["last_paused"]=current_pause
			if debate_data[f"{virtual_id}"]["last_paused"] and (not is_pause):
				debate_data[f"{virtual_id}"]["last_started"]=current_epoch
			current_status = debate_data[f"{virtual_id}"]["is_debate_running"]
			update_status = True if not is_pause else False
			debate_data[f"{virtual_id}"]["is_debate_running"] = update_status
			await redis.set(virtual_id, json.dumps(debate_data))
			await redis.close()
			msg = "Current Debate status is Active" if is_pause else "Current Debate status is In-Active"
			return {"msg":msg,"status":True,"is_pause":is_pause}
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

	'''
	Update Audience Count When audience join
	'''
	@staticmethod
	async def update_audience_count(virtual_id,join=True):
		redis = await get_redis_connection()
		exists = await redis.exists(virtual_id)
		if exists:
			data = await redis.get(virtual_id)
			debate_data = json.loads(data)
			total_viewer = debate_data[f"{virtual_id}"]["total_viewer"]
			if join:
				total_viewer = total_viewer+1
			if total_viewer>0 and (not join):
				total_viewer = total_viewer-1
			debate_data[f"{virtual_id}"]["total_viewer"] = total_viewer
			await redis.set(virtual_id, json.dumps(debate_data))
			await redis.close()
			msg = "Viewer Updated"
			return {"msg":msg,"total_viewer":total_viewer,"status":True}
		return {"msg":"Debate is not started yet","status":False}



	'''
		server participants avatar
	'''
	@staticmethod
	async def get_participant_avatar(team_name,virtual_id,db):
		from app.utils.common import get_virtual_id_fk
		userAvatars=[]
		redis = await get_redis_connection()
		exists = await redis.exists(virtual_id)
		# virtaul_id_fk = get_virtual_id_fk(virtual_id,db)
		# participantMaster = db.query(DebateParticipantMaster).filter(DebateParticipantMaster.user_id == user_id,DebateParticipantMaster.virtual_id == virtaul_id_fk,DebateParticipantMaster.is_active == True).first()
		# participantDetails = db.query(DebateParticipantDetail).filter(DebateParticipantDetail.participant_id  == participantMaster.id).first()
		# joinedTeam = participantDetails.joined_team
		# teamDetails = db.query(DebateParticipantTeamsDetailsMaster).filter(DebateParticipantTeamsDetailsMaster.team_id == joinedTeam,DebateParticipantTeamsDetailsMaster.is_active == True).first()
		# team_name = teamDetails.team_name
		if exists:
			data = await redis.get(virtual_id)
			debate_data = json.loads(data)
			team = debate_data[f"{virtual_id}"][team_name]
			user_ids = team["user_ids"]

			avatars = db.query(AvatarMaster).filter(AvatarMaster.user_id.in_(user_ids),AvatarMaster.is_active==True).all()
			for user in avatars:
				temp = {}
				temp["skin"] = user.skin_tone.image_path
				temp["hair"] = user.hair_colour.image_path
				temp["dress"] = user.dress_colour.image_path
				userAvatars.append(temp)
			return {"data":userAvatars,"status":True,"msg":""}
		return {"data":"","status":False,"msg":"No debate Exist!"}

	@staticmethod
	async def removeParticipantFromDebate(user_id,virtual_id,db):
		redis = await get_redis_connection()
		exists = await redis.exists(virtual_id)
		if exists:
			virtaul_id_fk = get_virtual_id_fk(virtual_id,db)
			participantMaster = db.query(DebateParticipantMaster).filter(DebateParticipantMaster.user_id == user_id,DebateParticipantMaster.virtual_id == virtaul_id_fk,DebateParticipantMaster.is_active == True).first()
			participantDetails = db.query(DebateParticipantDetail).filter(DebateParticipantDetail.participant_id  == participantMaster.id).first()
			joinedTeam = participantDetails.joined_team
			teamDetails = db.query(DebateParticipantTeamsDetailsMaster).filter(DebateParticipantTeamsDetailsMaster.team_id == joinedTeam,DebateParticipantTeamsDetailsMaster.is_active == True).first()
			team_name = teamDetails.team_name
			# import pdb;pdb.set_trace()
			data = await redis.get(virtual_id)
			debate_data = json.loads(data)
			team = debate_data[f"{virtual_id}"][team_name]
			user_ids = team["user_ids"]
			user_ids.remove(user_id)
			if not user_ids:
				user_ids=[]

			debate_data[f"{virtual_id}"][team_name]["user_ids"]=user_ids
			await redis.set(virtual_id, json.dumps(debate_data))
			await redis.close()
			#### Delete Participant ##
			db.delete(participantDetails)
			db.delete(participantMaster)
			db.commit()
			#######
			return {"msg":"User Has been Updated","status":True}
		return {"msg":"No Debate Exists","status":False}

	@staticmethod
	async def checkCurrentAndCompletedTopic(virtual_id,db):
		redis = await get_redis_connection()
		exists = await redis.exists(virtual_id)
		if exists:
			data = await redis.get(virtual_id)
			debate_data = json.loads(data)
			completedTopic = debate_data[f"{virtual_id}"]["completed_topic"]
			selectedTopic = debate_data[f"{virtual_id}"]["selected_topic"]
			return {"selected_topic":[selectedTopic],"compeleted_topic":completedTopic}
		raise f"No Debate Exists!"



	@staticmethod
	async def debateStartTime(virtual_id):
		redis = await get_redis_connection()
		exists = await redis.exists(virtual_id)
		if exists:
			data = await redis.get(virtual_id)
			debate_data = json.loads(data)
			startedTime =  debate_data[f"{virtual_id}"]["count_down_start"]
			lastPauseTime = debate_data[f"{virtual_id}"]["last_paused"]
			lastStartedTime = debate_data[f"{virtual_id}"]["last_started"]
			# start_from_last_pause = debate_data[f"{virtual_id}"]["start_from_last_pause"]
			return {"status":True,"startedTime":startedTime,"lastPauseTime":lastPauseTime,'lastStartedTime':lastStartedTime}
		return {"status":False,"startedTime":startedTime}

	@staticmethod
	async def set_start_from_last_pause(virtual_id):
		redis = await get_redis_connection()
		exists = await redis.exists(virtual_id)
		try:
			if exists:
				data = await redis.get(virtual_id)
				debate_data = json.loads(data)
				debate_data[f"{virtual_id}"]["start_from_last_pause"] = False
				await redis.set(virtual_id, json.dumps(debate_data))
				await redis.close()
				return {"status":True}
		except Exception as e:
			raise e

	@staticmethod
	async def resetDebateTime(virtual_id):
		redis = await get_redis_connection()
		exists = await redis.exists(virtual_id)
		if exists:
			data = await redis.get(virtual_id)
			debate_data = json.loads(data)
			debate_data[f"{virtual_id}"]["count_down_start"]=0
			debate_data[f"{virtual_id}"]["last_paused"]=0
			debate_data[f"{virtual_id}"]["last_started"]=0
			debate_data[f"{virtual_id}"]["is_debate_running"]=False
			await redis.set(virtual_id, json.dumps(debate_data))
			await redis.close()
			return {"status":True}
		return {"status":False}


	@staticmethod
	async def getDebateCurrentStatus(debate_id,db):
		debate_tracker = db.query(DebateTrackerMaster).filter(DebateTrackerMaster.debate_id == debate_id,DebateTrackerMaster.is_active == True).first()
		virtual_id = debate_tracker.virtual_id
		redis = await get_redis_connection()
		exists = await redis.exists(virtual_id)
		if exists:
			data = await redis.get(virtual_id)
			debate_data = json.loads(data)
			status = debate_data[f"{virtual_id}"]["is_debate_running"]
			return {"current_status":status,"msg":"Debate Started!"}
		return {"current_status":None,"msg":"Debate is not started yet"}

	@staticmethod
	async def set_participant_time_details(virtual_id,team_name,debate_type,topic_name):
		redis = await get_redis_connection()
		exists = await redis.exists(virtual_id)
		# import pdb;pdb.set_trace()
		if exists:
			data = await redis.get(virtual_id)
			debate_data = json.loads(data)
			for team in team_name:
				team_details = debate_data[f"{virtual_id}"][team][debate_type]
				if topic_name not in team_details.keys():
					# import pdb;pdb.set_trace()
					debate_data[f"{virtual_id}"][team][debate_type][topic_name]={}
					debate_data[f"{virtual_id}"][team][debate_type][topic_name]["is_pause"]=True
					debate_data[f"{virtual_id}"][team][debate_type][topic_name]["last_paused"]=0
					debate_data[f"{virtual_id}"][team][debate_type][topic_name]["is_completed"]=False
			# import pdb;pdb.set_trace()
			await redis.set(virtual_id, json.dumps(debate_data))
			await redis.close()
			return {"status":True}
		return {"status":False}

			# if topic not in team_details.keys():
			# 	team_details[topic_id]={"last_paused":0}
			# await redis.set(virtual_id, json.dumps(debate_data))
			# await redis.close()
			# if topic in teams_details.keys():
			# 	team_details[topic]={"last_paused":int(time.time())}
		# 	return {"status":True}
		# return {"status":False}

























