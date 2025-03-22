from fastapi import APIRouter, Depends, HTTPException, status
from app.api_v1.deps.db_deps import get_transaction_session
from sqlalchemy.orm import Session
from app.api_v1.deps.user_deps import get_current_user
from app.services.VoteServices import VoteService
from app.models.auth.UserMaster import UserMaster

vote_router = APIRouter()
@vote_router.get("/type",summary="Vote Type")
async def vote_type(db:Session=Depends(get_transaction_session),user:UserMaster=Depends(get_current_user)):
	try:
		return await VoteService.voteType(db)
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"{e}"
	)
