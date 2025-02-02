from enum import Enum

class DebateType(Enum):

	FREESTYLE='FREESTYLE'
	ADVANCE='ADVANCE'
	INTERMEDIATE='INTERMEDIATE'


class TeamSides(Enum):

	SIDE=['LEFT','RIGHT']

class ParticipantsType(Enum):

	DEBATER='DEBATER'
	AUDIENCE='AUDIENCE'
	MEDIATOR='MEDIATOR'