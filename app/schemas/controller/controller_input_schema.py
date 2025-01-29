from uuid import UUID
from pydantic import BaseModel,Field
from typing import Optional , Union , List


class LockParticipantsInputSchema(BaseModel):
	debate_id:int
	participant_type_id:int