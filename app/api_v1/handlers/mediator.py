from fastapi import APIRouter, Depends, HTTPException, status
from app.api_v1.deps.db_deps import get_transaction_session
from sqlalchemy.orm import Session
from app.api_v1.deps.user_deps import get_current_user
from app.services.MediatorServices import MediatorServices
from app.models.auth.UserMaster import UserMaster
mediator_router = APIRouter()
@mediator_router.get("/screen/details",summary="This api will provide topic list to meditor")
async def debateTopics(debate_id:int,virtual_id,db:Session=Depends(get_transaction_session),user:UserMaster=Depends(get_current_user)):
	try:
		return await MediatorServices.screenDetails(debate_id,virtual_id,db)
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"{e}"
		)

