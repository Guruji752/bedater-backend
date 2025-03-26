from uuid import UUID
from pydantic import BaseModel,Field
from typing import Optional , Union , List


class ParticipantInputSchema(BaseModel):
	debate_id:int
	virtual_id:Optional[str]=None
	participant_type_id:int
	joined_team:Optional[int]=None


class DebateParticipantsMasterInputSchema(BaseModel):
	debate_id:int
	participant_type_id:int
	user_id:int
	is_locked:bool
	virtual_id:Optional[int]=None