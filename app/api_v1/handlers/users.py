from fastapi import APIRouter, Depends, HTTPException, status
from app.api_v1.deps.db_deps import get_transaction_session
from sqlalchemy.orm import Session
from app.schemas.users.users_input_schema import UserSignupSchema
from app.services.UserServices import UserServices
from app.api_v1.deps.db import get_db
from app.api_v1.deps.db_deps import get_transaction_session
from app.api_v1.deps.user_deps import get_current_user
from app.schemas.auth.auth_schema import UserOut
from app.models.auth.UserMaster import UserMaster

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


@user_router.get('/me', summary='Get details of currently logged in user', response_model=UserOut)
async def get_me(user: UserMaster = Depends(get_current_user)):
    if user:
    	name = user.name
    	return {"isAuthenticated":True,"name":name}
    return {"isAuthenticated":False}
