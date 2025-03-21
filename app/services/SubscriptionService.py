from app.models.subscription.payment_details import PaymentDetail
from app.models.subscription.SubscriptionType import SubscriptionType
from app.models.subscription.UserSubscriptionDetails import UserSubscriptionDetail
from app.schemas.subscription.input_schema import CreateSubscription,PurchaseSubscriptionSchema,PaymentDetailsSchema
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder



class SubscriptionService:

	@staticmethod
	async def create_subscription(data,db,user):
		try:
			data_dict = data.dict()
			data_dict['created_by'] = user.id
			create_subscription_type = SubscriptionType(**data_dict)
			db.add(create_subscription_type)
			db.commit()
			db.refresh(create_subscription_type)
			return jsonable_encoder(create_subscription_type)
		except Exception as e:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail=f"{e}"
			)


	@staticmethod
	async def purchase(data,db,user):
		try:
			user_id = user.id
			payment_details = PaymentDetail(**data.dict())
			db.add(payment_details)
			db.flush()
			payment_id = payment_details.id
			subscription_details = data.dict()
			subscription_details['payment_details_id'] = payment_id
			subscription_details['user_id'] = user_id
			userSubscriptiondetails = PurchaseSubscriptionSchema(**subscription_details)
			user_subscription = UserSubscriptionDetail(**userSubscriptiondetails.dict())
			db.add(user_subscription)
			db.commit()
			return jsonable_encoder(user_subscription)
		except Exception as e:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail=f"{e}"
			)

	async def check_if_debate_allowed(user_id,db):
		userSubscription = db.query(UserSubscriptionDetail).filter(UserSubscriptionDetail.user_id == user_id,UserSubscriptionDetail.is_active == True).first()
		if not userSubscription:
			return {"allowed":False,"msg":f"No Active Subscription!"}
		used_debated = userSubscription.used_debated
		allowed_debate = userSubscription.subscription_type.allowed_debate
		if used_debated <= allowed_debate:
			userSubscription.used_debated+=1
			db.commit()
			db.refresh(userSubscription)
			return {"allowed":True,"msg":f"You have used {userSubscription.used_debated}"}
		userSubscription.is_active = False
		db.commit()
		return {"allowed":False,"msg":f"You have used all your debate"}
