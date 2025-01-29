from app.schemas.debate.debate_input_schema import TopicMasterInputSchema,CounterMasterStatementsInputSchema,AdvanceDebateDetailsMasterInputSchema,AdvacnceDebateTopicMasterInputSchema
from app.models.debate.CounterStatementsMaster import CounterStatementsMaster
from app.models.debate.TopicMaster import TopicMaster
from app.models.debate.AdvanceDebateDetailsMaster import AdvanceDebateDetailsMaster
from app.models.debate.AdvanceDebateTopicTimeMaster import AdvanceDebateTopicTimeMaster
from fastapi import status,HTTPException

class AdvanceStyleService:

	@staticmethod
	async def create_advance(data_dict,user_id,db):
		try:
			debate_id = data_dict['debate_id']
			counter_statments = data_dict['counter_statments']
			counter_statments['debate_id'] = data_dict['debate_id']
			counter_statments['created_by'] = user_id
			extra_details = data_dict['extra_details']
			counterDataSchema = CounterMasterStatementsInputSchema(**counter_statments)
			counterData = CounterStatementsMaster(**counterDataSchema.dict())
			db.add(counterData)
			topic_data = [{"topic":i['topic'],"debate_id":debate_id,"created_by":user_id} for i in extra_details]
			topics_master = [TopicMaster(**data) for data in topic_data]
			db.add_all(topics_master)
			db.flush()

			advance_debate_details_master = []
			for details in extra_details:
				temp ={}
				topic = details['topic']
				topic_id  = await AdvanceStyleService.get_topic_id_by_name(topic,topics_master)
				temp['topic_id'] = topic_id
				temp['debate_id'] = debate_id
				temp['action_side'] = details['action_side']
				temp['voting_type'] = details['voting_type']
				temp['voting_allowed'] = details['voting_allowed']
				temp['hour'] = details['hour']
				temp['minute'] = details['minutes']
				temp['seconds'] = details['seconds']
				temp['created_by'] = user_id
				advance_debate_details_master.append(temp)
			advance_debate_details_input = [AdvanceDebateDetailsMasterInputSchema(**data) for data in advance_debate_details_master]
			advance_debate_details = [AdvanceDebateDetailsMaster(**data.dict()) for data in advance_debate_details_input]
			db.add_all(advance_debate_details)
			advance_debate_topic_timer_master_input = [AdvacnceDebateTopicMasterInputSchema(**data) for data in advance_debate_details_master]
			advance_debate_topic_time_master = [AdvanceDebateTopicTimeMaster(**data.dict()) for data in advance_debate_topic_timer_master_input]
			db.add_all(advance_debate_topic_time_master)
			db.commit()
			return {"msg":"Debate has been created successfully","status":200}
		except Exception as e:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail=f"{e}"
			)

	@staticmethod
	async def get_topic_id_by_name(topic_name,topic_list):
		for topics in topic_list:
			if topics.topic == topic_name:
				return topics.id

