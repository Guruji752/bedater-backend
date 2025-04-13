import uuid
import random
import string
from app.models.debate.DebateTrackerMaster import DebateTrackerMaster
from app.models.debate.DebateMaster import DebateMaster
def generate_room_id():
	random_uuid = uuid.uuid4()
	return str(random_uuid)

def generate_codes():
	characters = string.ascii_uppercase + string.digits 
	participants_code = ''.join(random.choices(characters, k=5))
	audience_code = ''.join(random.choices(characters, k=5))
	return participants_code,audience_code


def generate_random_name():

	groups = {
	    "Harry Potter": ["The Marauders", "Dumbledore's Army", "Death Eaters"],
	    "Marvel": ["The Avengers", "X-Men", "Guardians of the Galaxy"],
	    "DC": ["Justice League", "Suicide Squad", "Teen Titans"],
	    "Stranger Things": ["The Party", "The Hellfire Club"],
	    "Star Wars": ["The Jedi Order", "The Sith Lords"],
	    "Peaky Blinders": ["The Shelby Company Ltd", "The Peaky Blinders"]
	}

	series = random.choice(list(groups.keys()))
	group_name = random.choice(groups[series])
	return group_name


def check_if_debate_allowed(user_id):
	userSubscription = db.query(UserSubscriptionDetail).filter(UserSubscriptionDetail.user_id == user_id,UserSubscriptionDetail.is_active == True).first()
	used_debated = userSubscription.used_debated
	allowed_debate = userSubscription.subscription_type.allowed_debate
	if used_debated <= allowed_debate:
		userSubscription.used_debated+=1
		db.commit()
		db.refresh(userSubscription)
		return True
	return False 


def get_virtual_id_fk(virtual_id,db):
	virtualId = db.query(DebateTrackerMaster).filter(DebateTrackerMaster.virtual_id == virtual_id,DebateTrackerMaster.is_active == True).first()
	_id = virtualId.id
	return _id

def get_room_id_of_debate(debate_id,db):
	debate = db.query(DebateMaster).filter(DebateMaster.id == debate_id,DebateMaster.is_active == True).first()
	room_id = debate.room_id
	return room_id


def string_to_bool(string_bool):
  if string_bool.lower() == 'true':
    return True
  elif string_bool.lower() == 'false':
    return False
  else:
    raise ValueError(f"Invalid boolean string: {string_bool}")
def get_debate_type(debate_id,db):
	try:
		debate = db.query(DebateMaster).filter(DebateMaster.id == debate_id,DebateMaster.is_active == True).first()
		debate_type = debate.debate_type.type
		return debate_type
	except Exception as e:
		raise e


def get_debate_team_name(debate_id,db):
	try:
		team = db.query(DebateParticipantTeamsDetailsMaster.team_name).filter(DebateParticipantTeamsDetailsMaster.debate_id == debate_id,DebateParticipantTeamsDetailsMaster.is_active == True).all()
		team_names = [t[0] for t in team]
		return team_names
	except Exception as e:
		raise e


