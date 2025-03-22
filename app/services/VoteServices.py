from app.models.vote.VoteTypeMaster import VoteTypeMaster
from fastapi.encoders import jsonable_encoder

class VoteService:

	@staticmethod
	async def voteType(db):
		vote_type = db.query(VoteTypeMaster).all()
		return jsonable_encoder(vote_type)
