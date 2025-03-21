from fastapi import APIRouter, Depends, HTTPException, status
from app.api_v1.deps.db_deps import get_transaction_session
from sqlalchemy.orm import Session
from app.api_v1.deps.user_deps import get_current_user
from app.models.subscription.payment_details import PaymentDetail
from app.models.subscription.SubscriptionType import SubscriptionType
from app.models.subscription.UserSubscriptionDetails import UserSubscriptionDetail
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status
from app.schemas.subscription.input_schema import CreateSubscription,PurchaseSubscriptionSchema,PaymentDetailsSchema
from app.services.SubscriptionService import SubscriptionService
from app.models.auth.UserMaster import UserMaster
subscription_router = APIRouter()


@subscription_router.post("/create",summary="This will create the subscription")
async def create_subscription(data:CreateSubscription,db:Session=Depends(get_transaction_session),user:UserMaster=Depends(get_current_user)):
	try:
		return await SubscriptionService.create_subscription(data,db,user)
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"{e}"
	)


@subscription_router.post("/purchase",summary="This api will purchase the subscription")
async def purchase_subscription(data:PaymentDetailsSchema,db:Session=Depends(get_transaction_session),user:UserMaster=Depends(get_current_user)):
	try:
		return await SubscriptionService.purchase(data,db,user)
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"{e}"
	)

@subscription_router.get("/check",summary="This api will check if subscription exist")
async def check_if_exist(db:Session=Depends(get_transaction_session),user:UserMaster=Depends(get_current_user)):
	try:
		user_id = user.id
		return await SubscriptionService.check_subscription(user_id,db)
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"{e}"
	)

