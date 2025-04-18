from sys import prefix
from fastapi import APIRouter
from app.api_v1.auth.jwt import auth_router
from app.api_v1.handlers.users import user_router
from app.api_v1.handlers.debates import debate_router
from app.api_v1.handlers.participants import participant_router
from app.api_v1.handlers.controller import controller_router
from app.api_v1.handlers.avatar import avatar_router
from app.api_v1.handlers.subscription import subscription_router
from app.api_v1.handlers.vote import vote_router
from app.api_v1.handlers.teams import teams_router
from app.api_v1.handlers.mediator import mediator_router
approuter = APIRouter()
approuter.include_router(auth_router,prefix='/auth',tags=["Auth"])
approuter.include_router(user_router,prefix='/user',tags=["User"])
approuter.include_router(debate_router,prefix='/debate',tags=["Debate"])
approuter.include_router(participant_router,prefix='/participant',tags=['Participant'])
approuter.include_router(controller_router,prefix="",tags=['Controller'])
approuter.include_router(avatar_router,prefix="/avatar",tags=['Avatar'])
approuter.include_router(subscription_router,prefix='/subscription',tags=['Subscription'])
approuter.include_router(vote_router,prefix='/vote',tags=['Vote'])
approuter.include_router(teams_router,prefix='/teams',tags=['Team'])
approuter.include_router(mediator_router,prefix='/meditor',tags=["Mediator"])