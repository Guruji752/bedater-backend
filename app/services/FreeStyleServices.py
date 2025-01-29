from app.schemas.debate.debate_input_schema import TopicMasterInputSchema,CounterMasterStatementsInputSchema
from app.models.debate.CounterStatementsMaster import CounterStatementsMaster
from app.models.debate.TopicMaster import TopicMaster
from fastapi import status,HTTPException
class FreeStyleServices:

	@staticmethod
	async def create_freestyle(data_dict,user_id,db):
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
			db.bulk_save_objects(topics_master)
			db.commit()
			return {"msg":"Debate has been created successfully","status":200}
		except Exception as e:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail=f"{e}"
		)










