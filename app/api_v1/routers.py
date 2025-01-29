from sys import prefix
from fastapi import APIRouter
from app.api_v1.auth.jwt import auth_router
from app.api_v1.handlers.users import user_router
from app.api_v1.handlers.debates import debate_router

approuter = APIRouter()
approuter.include_router(auth_router,prefix='/auth',tags=["Auth"])
approuter.include_router(user_router,prefix='/user',tags=["User"])
approuter.include_router(debate_router,prefix='/debate',tags=["Debate"])
