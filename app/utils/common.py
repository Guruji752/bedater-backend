import uuid
import random
import string


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

