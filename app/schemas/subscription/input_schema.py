from uuid import UUID
from pydantic import BaseModel,Field
from typing import Optional , Union , List,Optional

class CreateSubscription(BaseModel):
	plan_name:str
	amount:float
	debate_type:int
	allowed_debate:int

class PurchaseSubscriptionSchema(BaseModel):
	user_id:int
	subscription_type_id:int
	payment_details_id:int
	used_debated:Optional[int]=0



class PaymentDetailsSchema(BaseModel):
	transiction_id:str
	subscription_type_id:int


