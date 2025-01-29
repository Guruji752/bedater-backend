from fastapi import APIRouter, Depends, HTTPException, status
from app.api_v1.deps.db_deps import get_transaction_session
from sqlalchemy.orm import Session
from app.schemas.users.users_input_schema import UserSignupSchema
from app.services.UserServices import UserServices
from app.api_v1.deps.db import get_db
from app.api_v1.deps.db_deps import get_transaction_session



user_router = APIRouter()
@user_router.post("/signup",summary="Create User")
async def create_user(data:UserSignupSchema,db:Session=Depends(get_db)):
	try:
		return await UserServices.create_user(data,db)
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"{e}"
		)