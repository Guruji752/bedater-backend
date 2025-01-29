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

