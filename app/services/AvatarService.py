from app.settings.config import settings
from fastapi import HTTPException,status
from app.models.avatar.AvatarMaster import AvatarMaster
from app.utils.enums import DocumentType,GenderType
from app.models.general.ImageTypeMaster import ImageTypeMaster
from app.models.general.ImageMaster import ImageMaster

class AvatarService:

	@staticmethod
	async def creatAvatar(data,db,user):
		data_dict = data.dict()
		user_id = user.id
		data_dict["user_id"] = user_id
		check_if_exist = db.query(AvatarMaster).filter(AvatarMaster.user_id == user_id,AvatarMaster.is_active == True).first()
		if check_if_exist:
			check_if_exist.is_active = False
		avatar_details = AvatarMaster(**data_dict)
		db.add(avatar_details)
		db.commit()
		db.refresh(avatar_details)
		return {"msg":"Avatar has been created!","status":200}

	
	@staticmethod
	async def getAvatar(user,db):
		user_id = user.id
		avatar_master = db.query(AvatarMaster).filter(AvatarMaster.user_id == user_id,AvatarMaster.is_active == True).all()
		avatar = {"skin":"","hair":"","dress":""}
		for i in avatar_master:
			if i.skin_tone.image_type_master.type ==  DocumentType.SKIN.value:
				avatar["skin"] = i.skin_tone.image_path
			if i.hair_colour.image_type_master.type == DocumentType.MALEHAIR.value:
				avatar["hair"] = i.hair_colour.image_path
			if i.dress_colour.image_type_master.type == DocumentType.DRESS.value:
				avatar["dress"] = i.dress_colour.image_path
			return avatar
			
	@staticmethod
	async def listAvatarBody(gender,db):
		'''
		avata_body:{"hair":[],"dress":[],"skin":[]}
		'''
		output = {"skin":[],"hair":[],"dress":[]}
		gender = gender.upper()
		hair_type = DocumentType.MALEHAIR.value if gender == GenderType.MALE.value else DocumentType.FEMAILHAIR.value
		filter_data = [hair_type,DocumentType.SKIN.value,DocumentType.DRESS.value]
		image_types = db.query(ImageTypeMaster.id).filter(ImageTypeMaster.type.in_(filter_data)).all()
		image_type_id = [i[0] for i in image_types]
		images = db.query(ImageMaster).filter(ImageMaster.image_type.in_(image_type_id)).all()

		for image in images:
			image_path = image.image_path
			if image.image_type_master.type == DocumentType.SKIN.value:
				output['skin'].append({"image_path":image_path,"id":image.id})
			if image.image_type_master.type == hair_type:
				output['hair'].append({"image_path":image_path,"id":image.id})
			if image.image_type_master.type == DocumentType.DRESS.value:
				output['dress'].append({"image_path":image_path,"id":image.id})
		return output











