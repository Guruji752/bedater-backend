from app.settings.config import settings
from fastapi import HTTPException,status
from app.models.debate.DebateParticipantTeamsMaster import DebateParticipantTeamsMaster
from app.models.debate.DebateParticipantTeamsDetailsMaster import DebateParticipantTeamsDetailsMaster
from app.utils.common import get_virtual_id_fk
from fastapi.encoders import jsonable_encoder

class TeamsDetailsServices:

	@staticmethod
	async def teamsDetails(virtual_id,db,user):
		virtual_id_fk = get_virtual_id_fk(virtual_id,db)
		team_details = db.query(DebateParticipantTeamsDetailsMaster).filter(DebateParticipantTeamsDetailsMaster.virtual_id == virtual_id_fk,DebateParticipantTeamsDetailsMaster.is_active == True).all()
		return jsonable_encoder(team_details)
