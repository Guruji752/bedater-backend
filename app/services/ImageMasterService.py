from app.models.general.ImageTypeMaster import ImageTypeMaster
from app.utils.enums import DocumentType
from app.models.general.ImageMaster import ImageMaster

class ImageMasterService:

	@staticmethod
	async def create_image(image_name,image_path,image_type,user_id,db):
		image_type_details = db.query(ImageTypeMaster).filter(ImageTypeMaster.type == image_type).first()
		image_type_id = image_type_details.id
		data = {"image_name":image_name,"image_path":image_path,"image_type":image_type_id,"created_by":user_id}
		image_master = ImageMaster(**data)
		db.add(image_master)
		db.commit()
		db.refresh(image_master)
		return {"msg":"Image has been uploaded!","status":200}





		