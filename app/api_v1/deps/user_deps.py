from fastapi.security import OAuth2PasswordBearer
from app.settings.config import settings
from app.schemas.auth.auth_schema import TokenPayload
from fastapi import Depends,HTTPException,status,Request
from jose import jwt
from pydantic import ValidationError
from datetime import datetime
from sqlalchemy.orm import Session
import json
from app.api_v1.deps.db import get_db




reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    scheme_name="JWT"
)

async def get_current_user(request: Request, token: str = Depends(reuseable_oauth), db: Session = Depends(get_db)):
    try: 
        from app.services.AuthServices import AuthServices
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except(jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_data = token_data.sub
    obj = token_data.replace("'", '"').replace("None", "null").replace("False", "false").replace("True", "true")
    obj = json.loads(obj)

    # username =  None
   
    user_id = obj["user_id"]
    user = await AuthServices.get_user_by_user_id(user_id, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )
    
    return user


