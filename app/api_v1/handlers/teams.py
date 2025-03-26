from fastapi import APIRouter, Depends, HTTPException, status
from app.api_v1.deps.db_deps import get_transaction_session
from sqlalchemy.orm import Session
from app.api_v1.deps.user_deps import get_current_user
from app.services.TeamsDetailsServices import TeamsDetailsServices
from app.models.auth.UserMaster import UserMaster

teams_router = APIRouter()

@teams_router.get("/details/{virtual_id}",summary="This Api Will Fetch team details for started deabte on basis of virtual id")
async def team_detals(virtual_id:str,db:Session=Depends(get_transaction_session),user:UserMaster=Depends(get_current_user)):
	try:
		return await TeamsDetailsServices.teamsDetails(virtual_id,db,user)
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"{e}"
			)

