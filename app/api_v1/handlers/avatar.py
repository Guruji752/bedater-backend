from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from app.api_v1.deps.db_deps import get_transaction_session
from sqlalchemy.orm import Session
from app.api_v1.deps.user_deps import get_current_user
from app.models.auth.UserMaster import UserMaster
from app.services.AvatarService import AvatarService
from app.schemas.avatar.avatar_input_schema import AvatarInputSchema

avatar_router = APIRouter()

@avatar_router.post("/create",summary="Create Avatar")
async def create_avatar(data:AvatarInputSchema,db:Session=Depends(get_transaction_session),user:UserMaster=Depends(get_current_user)):
	try:
		return await AvatarService.creatAvatar(data,db,user)
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"{e}"
		)


@avatar_router.get("/",summary="Get Avatar")
async def get_avatar(db:Session=Depends(get_transaction_session),user:UserMaster=Depends(get_current_user)):
	try:
		return await AvatarService.getAvatar(user,db)
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"{e}"
		)

@avatar_router.get("/avatar/list/body/{gender}",summary="list all the avatar bodies")
async def list_avatar_body(gender:str,db:Session=Depends(get_transaction_session),user:UserMaster=Depends(get_current_user)):
	try:
		return await AvatarService.listAvatarBody(gender,db)
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"{e}"
		)


