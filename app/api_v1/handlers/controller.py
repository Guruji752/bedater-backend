from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from app.api_v1.deps.db_deps import get_transaction_session
from sqlalchemy.orm import Session
from app.api_v1.deps.user_deps import get_current_user
from app.schemas.controller.controller_input_schema import LockParticipantsInputSchema,CheckDebateStart
from app.models.auth.UserMaster import UserMaster
from app.services.ControllerServices import ControllerServices
import uuid
from app.services.UploadServices import S3Services
from app.api_v1.deps.form_deps import parse_form_data
from app.models.debate.DebateMaster import DebateMaster
from app.models.debate.DebateTrackerMaster import DebateTrackerMaster

controller_router = APIRouter()

@controller_router.post("/lock/participants",summary="It will lock all debater and meditor")
async def lock_participants(data:LockParticipantsInputSchema,db:Session=Depends(get_transaction_session),user:UserMaster=Depends(get_current_user)):
	try:
		return await ControllerServices.lock_participants_service(data,user,db)
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"{e}"
		)


@controller_router.post("/upload",summary="Use This api to upload any type of image in s3")
async def upload_images(form_data:dict = Depends(parse_form_data),db:Session=Depends(get_transaction_session),user:UserMaster=Depends(get_current_user)):
	try:
		s3_service  = S3Services()
		uploaded_path = await s3_service.upload_file(form_data,db,user)
		return {"file_path":uploaded_path['file_url']}
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"{e}"
		)

@controller_router.post("/check/debate/start",summary="This Api will check if mediator has started the debate and it will be integrated one debaters/audience will enter the code")
async def check_debate_start(data:CheckDebateStart,db:Session=Depends(get_transaction_session)):
	try:

		return await ControllerServices.checkDebateStart(data,db)
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"{e}"
		)

