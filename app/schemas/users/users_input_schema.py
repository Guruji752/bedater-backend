from pydantic import BaseModel,Field,EmailStr , validator,root_validator
from typing import Optional , Union


class UserSignupSchema(BaseModel):
	username:str
	email:EmailStr
	name:str
	gender:str
	phone_no:str
	password:str


class UserDetailsSchema(BaseModel):
	username:str
	email:EmailStr
	name:str
	gender:str
	phone_no:str

class UserPasswordSchema(BaseModel):
	password:str
	user_id:int

