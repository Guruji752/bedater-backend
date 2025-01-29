import os
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any
from pydantic import ValidationError
from jose import jwt
from app.settings.config import settings
from app.schemas.auth.auth_schema import TokenSchema,UserOut,TokenPayload
from app.api_v1.deps.db import get_db
from app.settings.security import create_access_token,create_refresh_token
from fastapi.encoders import jsonable_encoder
from app.services.AuthServices import AuthServices
from app.api_v1.deps.user_deps import get_current_user



auth_router = APIRouter()
@auth_router.post('/login', summary="Create access and refresh tokens for user", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),db_session=Depends(get_db)) -> Any:
    username = form_data.username
    password = form_data.password
    user = await AuthServices.authenticate(username=form_data.username, password=form_data.password,db=db_session)
    user_obj = {"email":user.email,"username":user.username,"user_id":user.id}
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    return {
        "access_token": create_access_token(user_obj),
        "refresh_token": create_refresh_token(user_obj),

    }

@auth_router.post('/refresh', summary="Refresh token", response_model=TokenSchema)
async def refresh_token(refresh_token: str = Body(...),db=Depends(get_db)):
    try:
        payload = jwt.decode(
            refresh_token, settings.JWT_REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await AuthServices.get_user_by_username(token_data.sub,db)
    user_obj = {"email":user.email,"username":user.username,"user_id":user.id}

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid token for user",
        )
    return {
        "access_token": create_access_token(user_obj),
        "refresh_token": create_refresh_token(user_obj),
    }
