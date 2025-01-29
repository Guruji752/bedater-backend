from fastapi import APIRouter, Depends, HTTPException, status
from app.api_v1.deps.db_deps import get_transaction_session
from sqlalchemy.orm import Session
from app.api_v1.deps.user_deps import get_current_user
from app.schemas.controller.controller_input_schema import LockParticipantsInputSchema
from app.models.auth.UserMaster import UserMaster
from app.services.ControllerServices import ControllerServices

controller_router = APIRouter()

@controller_router.post("/lock/participants",summary="It will lock all debater and meditor")
async def lock_participants(data:LockParticipantsInputSchema,db:Session=Depends(get_transaction_session),user:UserMaster=Depends(get_current_user)):
	try:
		return await ControllerServices.lock_participants_service(data,user,db)
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"{e}"
		)