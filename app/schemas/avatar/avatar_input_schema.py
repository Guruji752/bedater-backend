from uuid import UUID
from pydantic import BaseModel,Field,validator
from typing import Optional , Union , List

class AvatarInputSchema(BaseModel):
	gender:str
	skin_tone_id:int
	hair_colour_id:int
	dress_colour_id:int
	is_active:Optional[bool]=True

	@validator("gender",pre=True,always=True)
	def capitalize_gender(cls,value):
		return value.upper() if isinstance(value,str) else value

