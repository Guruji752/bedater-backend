from app.settings.config import settings
from app.utils.enums import DocumentType
from app.services.ImageMasterService import ImageMasterService
import boto3
from fastapi import HTTPException,status
import uuid

class S3Services:

	def __init__(self):
		self.AWS_ACCESS_KEY = settings.AWS_ACCESS_KEY
		self.AWS_SECRET_KEY = settings.AWS_SECRET_KEY
		self.AWS_BUCKET_NAME = settings.AWS_BUCKET_NAME
		self.AWS_REGION = settings.AWS_REGION

		# self.AWS_BUCKET_NAME = bucket_name
		self.s3_client = boto3.client(
			"s3",
			aws_access_key_id=self.AWS_ACCESS_KEY,
			aws_secret_access_key=self.AWS_SECRET_KEY,
			region_name=self.AWS_REGION,

		)

	async def upload_file(self,form_data,db,user):
		try:
			user_id = user.id
			file_obj = form_data['file']
			doc_type = form_data['doc_type']
			file_name = form_data['file_name']
			if doc_type.upper() in [DocumentType.MALEHAIR.value,DocumentType.SKIN.value,DocumentType.DRESS.value,DocumentType.FEMALEHAIR.value]:
				folder = settings.AVATAR_IMAGE_FOLDER_NAME
			if not file_name:
				file_extension = file_obj.filename.split(".")[-1]
				file_name = f"{uuid.uuid4()}.{file_extension}"
			fileName = f"{folder}/{file_name}"
			self.s3_client.upload_fileobj(file_obj.file, self.AWS_BUCKET_NAME, fileName)
			
			file_url = f"https://{self.AWS_BUCKET_NAME}.s3.{self.AWS_REGION}.amazonaws.com/{folder}/{file_name}"
			image_details = await ImageMasterService.create_image(file_name,file_url,doc_type,user_id,db)
			return {"file_url": file_url}
		except Exception as e:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail=f"{e}"
			)










