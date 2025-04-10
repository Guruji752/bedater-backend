from fastapi import APIRouter, Depends, HTTPException, status
from app.api_v1.deps.db_deps import get_transaction_session
from sqlalchemy.orm import Session
from app.schemas.debate.debate_input_schema import CreateDebateInputSchema
from app.api_v1.deps.user_deps import get_current_user
from app.models.auth.UserMaster import UserMaster
from app.services.DebateServices import DebateServices
from app.services.RedisServices import RedisServices
debate_router = APIRouter()

@debate_router.post("/create",summary="Create Debate")
async def create_debate(data:CreateDebateInputSchema,db:Session=Depends(get_transaction_session),user:UserMaster = Depends(get_current_user)):
	try:
		return await DebateServices.create_debate_service(data,db,user)
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"{e}"
	)


@debate_router.put("/update",summary="Edit debate")
async def update_debate(db:Session=Depends(get_transaction_session)):
	try:
		pass
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"{e}"
	)


@debate_router.delete("/delete",summary="Delete Debate")
async def delete_debate(db:Session=Depends(get_transaction_session)):
	try:
		pass
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"{e}"
	)

@debate_router.get("/list/{debate_status_type_id}",summary="List all type of debate")
async def list_debate(debate_status_type_id:int,user:UserMaster=Depends(get_current_user),db:Session=Depends(get_transaction_session)):
	try:
		return await DebateServices.listDebates(debate_status_type_id,user,db)
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"{e}"
	)

@debate_router.put("/save",summary="Save the debate")
async def save_debate(debate_id:int,user:UserMaster=Depends(get_current_user),db:Session=Depends(get_transaction_session)):
	try:
		return await DebateServices.saveDebates(debate_id,user,db)
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"{e}"
	)


@debate_router.get("/type",summary="Debate Type")
async def debate_type(db:Session=Depends(get_transaction_session)):
	try:
		return await DebateServices.debateType(db)
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"{e}"
	)


@debate_router.get("/allowed",summary="Debates allowed to user on basis of subscription")
async def allowed_debate_type(user:UserMaster=Depends(get_current_user),db:Session=Depends(get_transaction_session)):
	try:
		user_id = user.id
		return await DebateServices.allowedDebateType(user_id,db)
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"{e}"
	)

@debate_router.get("/current_status/{debate_id}",summary="Api to give current status")
async def get_current_status(debate_id:int,db:Session=Depends(get_transaction_session)):
	try:
		return await RedisServices.getDebateCurrentStatus(debate_id,db)
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"{e}"
	)


