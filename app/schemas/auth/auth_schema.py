from uuid import UUID
from pydantic import BaseModel
# from app.models.auth.UserMaster import UserMaster

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    
    
class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None


class UserOut(BaseModel):
    employee_code_id:int = None