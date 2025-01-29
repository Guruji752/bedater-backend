from app.models.auth.UserMaster import UserMaster
from app.models.auth.PasswordMaster import PasswordMaster
from app.settings.security import verify_password
import re


class AuthServices:

	@staticmethod
	async def authenticate(username:str,password:str,db):
		email_regex = re.compile(
			r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
		)
		check_if_email = re.match(email_regex, username)
		if check_if_email:
			user = await AuthServices.get_user_by_id(username,db)
			if user:
				user_id = user.id
		else:
			user = await AuthServices.get_user_by_username(username,db)
			if user:
				user_id = user.id
		if not user:
			return None

		hash_password = await AuthServices.get_user_password(user_id,db)
		if not verify_password(password=password, hashed_pass=hash_password):
			return None
		return user

	

	@staticmethod
	async def get_user_by_email_id(email_id:str,db):
		employee = db.query(UserMaster).filter(UserMaster.email == email_id,UserMaster.is_active==True).first()
		if employee and employee.is_active:
			return employee

	@staticmethod
	async def get_user_by_username(username:str,db):
		employee = db.query(UserMaster).filter(UserMaster.username == username,UserMaster.is_active==True).first()
		if employee and employee.is_active:
			return employee

	@staticmethod
	async def get_user_by_user_id(user_id:str,db):
		employee = db.query(UserMaster).filter(UserMaster.id == user_id,UserMaster.is_active==True).first()
		if employee and employee.is_active:
			return employee

	@staticmethod
	async def get_user_password(user_id:str,db):
		details =  db.query(PasswordMaster).filter(PasswordMaster.user_id  == user_id,PasswordMaster.is_active==True).first()
		if details.is_active:
			return details.password


