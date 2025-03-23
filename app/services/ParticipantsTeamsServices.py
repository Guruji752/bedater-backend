from app.models.debate.DebateParticipantTeamsDetailsMaster import DebateParticipantTeamsDetailsMaster
from app.utils.enums import TeamSides 
from app.utils.common import generate_random_name
from fastapi.encoders import jsonable_encoder
from fastapi import status,HTTPException
from app.models.debate.DebateParticipantTeamsMaster import DebateParticipantTeamsMaster
from app.models.debate.DebateTrackerMaster import DebateTrackerMaster
from app.utils.common import get_virtual_id_fk
class ParticipantsTeamsServices:

	@staticmethod
	async def create_participant_team_master(debate_id,user_id,db):
		try:
			data = {"debate_id":debate_id,"created_by":user_id}
			teams_details_list = []
			teams_name = []
			teams_data = []
			is_exist = True
			for side in TeamSides.SIDE.value:
				temp={}
				temp = data.copy()
				temp['team_side']=side
				teams_details_list.append(temp)
			teams_detail_master = [DebateParticipantTeamsMaster(**data) for data in teams_details_list]
			db.add_all(teams_detail_master)
			db.flush()
			for i in teams_detail_master:
				temp={}
				temp['team_side'] = i.team_side
				temp['team_id'] = i.id
				teams_data.append(temp)
			return {"msg":"Team has been created","status":True,'data':teams_data}
		except Exception as e:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail=f"{e}"
			)



	@staticmethod
	async def create_participant_teams_details_2(debate_id,created_by,db):
		try:
			data = {"debate_id":debate_id,"created_by":created_by}
			teams_details_list = []
			teams_name = []
			teams_data = []
			is_exist = True
			for side in TeamSides.SIDE.value:
				temp={}
				temp = data.copy()
				name = generate_random_name()
				while is_exist:
					name = generate_random_name()
					if name not in teams_name:
						teams_name.append(name)
						is_exist=False
					# break
					# teams_data.append(name)
				temp['team_name']=name
				temp['team_side']=side
				teams_details_list.append(temp)
			
			print(teams_details_list)	
			teams_detail_master = [DebateParticipantTeamsDetailsMaster(**data) for data in teams_details_list]
			db.add_all(teams_detail_master)
			db.flush()
			for i in teams_detail_master:
				temp={}
				temp['team_side'] = i.team_side
				temp['team_id'] = i.id
				temp['name'] = i.team_name
				teams_data.append(temp)
			return {"msg":"Team has been created","status":True,'data':teams_data}
		except Exception as e:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail=f"{e}"
			)

			




	@staticmethod
	async def create_participant_team_details(debate_id,virtual_id,user_id,db):
		try:
			virtual_fk_id = get_virtual_id_fk(virtual_id,db)
			### check if team exist already for the debate ##
			debateTeams = db.query(DebateParticipantTeamsDetailsMaster).filter(DebateParticipantTeamsDetailsMaster.virtual_id == virtual_fk_id,DebateParticipantTeamsDetailsMaster.is_active == True).all()
			if debateTeams:
				return {"msg":"Teams Already Exists"}
			#######################################
			teams = db.query(DebateParticipantTeamsMaster).filter(DebateParticipantTeamsMaster.debate_id == debate_id,DebateParticipantTeamsMaster.is_active == True).all()
			
			debateTrackerDetails = db.query(DebateTrackerMaster).filter(DebateTrackerMaster.virtual_id == virtual_id,DebateTrackerMaster.is_active == True).first()
			virtual_id_fk = debateTrackerDetails.id
			teams_name = []
			teams_details_list = []
			for team in teams:
				temp = {}
				name = generate_random_name()
				if name in teams_details_list:
					name = generate_random_name()
				temp['team_name']=name
				temp['team_id']=team.id
				temp["debate_id"] = debate_id
				temp["virtual_id"]=virtual_id_fk
				temp["created_by"]=user_id
				teams_details_list.append(temp)
			teams_detail_master = [DebateParticipantTeamsDetailsMaster(**data) for data in teams_details_list]
			db.add_all(teams_detail_master)
			db.commit()
			return {"msg":"Teams Created"}
		except Exception as e:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail=f"{e}"
			)






