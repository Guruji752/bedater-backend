from app.models.debate.DebateParticipantTeamsDetailsMaster import DebateParticipantTeamsDetailsMaster
from app.utils.enums import TeamSides 
from app.utils.common import generate_random_name
from fastapi.encoders import jsonable_encoder
from fastapi import status,HTTPException


class ParticipantsTeamsServices:

	@staticmethod
	async def create_participant_teams_details(debate_id,created_by,db):
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

			
