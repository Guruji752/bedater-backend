from app.schemas.users.users_input_schema import UserSignupSchema,UserDetailsSchema,UserPasswordSchema
from app.models.auth.UserMaster import UserMaster
from app.models.auth.PasswordMaster import PasswordMaster
from fastapi.encoders import jsonable_encoder
import bcrypt
import hashlib



class UserServices:

	@staticmethod
	async def create_user(data:UserSignupSchema,db):
		dict_data = data.dict()
		user_data = UserDetailsSchema(**data.dict())
		user = UserMaster(**user_data.dict())
		password = dict_data['password']
		hash_password = hashlib.md5(password.encode('utf-8')).hexdigest()
		try:
			db.add(user)
			db.flush()
			dict_data['user_id'] = user.id
			dict_data['password'] = hash_password
			password_data = UserPasswordSchema(**dict_data)
			password = PasswordMaster(**password_data.dict())
			db.add(password)
			db.commit()
			db.refresh(user)
			return jsonable_encoder(user)
		except Exception as e:
			raise (e)
	
