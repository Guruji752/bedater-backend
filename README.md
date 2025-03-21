### code flow ####

##### USER AUTH / CREATION  #####

User can login using username or email id.

API's

/login,/singup,/refresh
/me (This api gives user details like isAuthenticated and etc.)

######################

#### AVATAR ########

1) Users like participant and mediator can create there own avatar.
2) All avatar skins will be uploaded to s3 before hand using "/upload" API
3) API's
	/avatar/create(to create),  /avatar/(to fetch )

###################

##### CREATE DEBATE JOURNEY ###

1) PUT debate type in DEBATEMASTER before hand
2) 


##### Debate Status Flow#####

1) When debate will be create it will get save with status UPCOMING in DebateStatusMaster
2) If user will mark debate as save then it will update the upcoming status of debate to save
3) once Debate will be finished a new entry will come into DebateStatusMaster and if entry is already there then it will update the last_updated column

### Participant Flow ####

1) Participants are the debater
2) We will create a new participant every time for user for every debate
 in DebateParticipantMaster
3) And while creating participant we'll check if user is already not a part of any debate 
4) We'll mark participant and mediator locked once debate will start in 
DebateParticipantMaster




#### Websocker Flow ####

1) Websocket will be connect once users will be locked
2) 


