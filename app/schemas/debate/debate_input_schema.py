from uuid import UUID
from pydantic import BaseModel,Field
from typing import Optional , Union , List


class CreateDebateBaseInputSchema(BaseModel):
	debate_type_id:int
	title:str
	hour:str
	minute:str
	seconds:str
	member_on_each_side:int


class CounterStatementsInputSchema(BaseModel):
	# debate_id:int
	counters:int
	seconds:str

class DebateExtraDetailsInput(BaseModel):
	topic:str
	action_side:Optional[str]=None
	voting_type:Optional[int]=None
	voting_allowed:Optional[bool]=None
	hour:Optional[str]=None
	minutes:Optional[str]=None
	seconds:Optional[str]=None


class CreateDebateInputSchema(BaseModel):
	# topic:List[str] = Field(...,description="list of topics")
	common_details:CreateDebateBaseInputSchema
	counter_statments:CounterStatementsInputSchema
	extra_details:List[DebateExtraDetailsInput]


class DebateMasterInputSchema(BaseModel):
	debate_type_id:int
	title:str
	room_id:str
	hour:str
	minute:str
	seconds:str
	debate_status_type_id:int
	member_on_each_side:int
	participants_code:str
	audience_code:str
	created_by:int


class TopicMasterInputSchema(BaseModel):
	debate_id:int
	topic:str
	created_by:int


class CounterMasterStatementsInputSchema(BaseModel):
	debate_id:int
	counters:int
	seconds:int
	created_by:int

class AdvanceDebateDetailsMasterInputSchema(BaseModel):
	debate_id:int
	topic_id:int
	team_id:int
	voting_type:int
	voting_allowed:bool
	created_by:int

class AdvacnceDebateTopicMasterInputSchema(BaseModel):
	debate_id:int
	topic_id:int
	hour:str
	minute:str
	seconds:str
	created_by:int




