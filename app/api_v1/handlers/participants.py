from fastapi import APIRouter, Depends, HTTPException, status
from app.api_v1.deps.db_deps import get_transaction_session
from sqlalchemy.orm import Session
from app.api_v1.deps.user_deps import get_current_user
from app.services.ParticipantsServices import ParticipantsService
from app.schemas.participant.participant_input_schema import ParticipantInputSchema
from app.models.auth.UserMaster import UserMaster

participant_router = APIRouter()

@participant_router.post("/create",summary="Create Participant")
async def create_participant(data:ParticipantInputSchema,db:Session=Depends(get_transaction_session),user:UserMaster=Depends(get_current_user)):
	try:
		return await ParticipantsService.create_participants_service(data,db,user)
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"{e}"
	)
