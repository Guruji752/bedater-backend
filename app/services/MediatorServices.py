from app.models.debate.DebateMaster import DebateMaster
from app.models.debate.DebateTypeMaster import DebateTypeMaster
from app.models.debate.TopicMaster import TopicMaster
from app.models.debate.AdvanceDebateTopicTimeMaster import AdvanceDebateTopicTimeMaster
from app.services.RedisServices import RedisServices
from app.utils.enums import DebateType
from app.utils.common import get_virtual_id_fk
from app.models.debate.DebateTrackerMaster import DebateTrackerMaster
from app.services.RedisServices import RedisServices
import time
# from app.utils.common import convert_epoch_difference
from app.models.debate.DebateParticipantTeamsDetailsMaster import DebateParticipantTeamsDetailsMaster
class MediatorServices:

    @staticmethod
    async def screenDetails(debate_id, db):
        debateTracker = db.query(DebateTrackerMaster).filter(DebateTrackerMaster.debate_id == debate_id,DebateTrackerMaster.is_active == True).first()
        virtual_id = debateTracker.virtual_id
        selected_topic, completed_topic = await RedisServices.checkCurrentAndCompletedTopic(virtual_id, db)
        
        debate = db.query(DebateMaster).filter(
            DebateMaster.id == debate_id, DebateMaster.is_active == True
        ).first()
        debateTitle = debate.title
        if not debate:
            return []
        
        debate_type = debate.debate_type.type
        topics = db.query(TopicMaster).filter(TopicMaster.debate_id == debate_id).all()
        Topic = []

        def add_topics(topic_list,debate_type,debate_id=debate_id,virtual_id=virtual_id,hour=0, minute=0, second=0):
            data = []
            for t in topic_list:
                is_complete = True if t.topic.topic in completed_topic else False
                is_selected = True if t.topic.topic in selected_topic else False
                is_pending = True if not (is_complete or is_selected) else False
                _topic_id = t.id if debate_type != DebateType.ADVANCE.value else t.topic_id
                data.append({
                    "id":_topic_id,
                    "title": t.topic.topic,
                    "hour": hour,
                    "minute": minute,
                    "second": second,
                    "debate_id":debate_id,
                    "virtual_id":virtual_id,
                    "is_complete": is_complete,
                    "is_pending": is_pending,
                    "is_selected": is_selected
                })
            return data
        if debate_type in {DebateType.FREESTYLE.value, DebateType.INTERMEDIATE.value}:
            Topic.extend(add_topics(topics,debate_type))
        elif debate_type == DebateType.ADVANCE.value:
            advance_topics = db.query(AdvanceDebateTopicTimeMaster).filter(
                AdvanceDebateTopicTimeMaster.debate_id == debate_id
            ).all()
            for t in advance_topics:
            	data = add_topics(advance_topics,debate_type, hour=t.hour , minute=t.minute , second=t.seconds)

            Topic.extend(
                data
            )
        vk_fk = get_virtual_id_fk(virtual_id,db)

        team1,team2 = db.query(DebateParticipantTeamsDetailsMaster.team_name).filter(DebateParticipantTeamsDetailsMaster.debate_id == debate_id ,DebateParticipantTeamsDetailsMaster.virtual_id == vk_fk).all()
        
        return {"team1":team1[0],"team2":team2[0],"topic":Topic,"debate_title":debateTitle}

    @staticmethod
    async def mediatorDebateTimer(debate_id,virtual_id,is_pause,is_refresh,db):
        
        debateTime= await RedisServices.debateStartTime(virtual_id)
        print(debateTime,"=======from Redis======")
        if not debateTime["status"]:
            return {"status":False}
        debate = db.query(DebateMaster).filter(DebateMaster.id == debate_id, DebateMaster.is_active == True).first()
        # Get the original total duration from debate object
        total_hour = int(debate.hour)
        total_minute = int(debate.minute)
        total_second = int(debate.seconds)

        ####
        # CASE 1 ### Debate Not started and user keep refresh or First time Load #is_Pause : True
        # print(is_refresh,is_pause,"==========")
        if is_refresh and is_pause and (not debateTime["startedTime"]):
            print("CASE1")
            return total_hour, total_minute, total_second
        #######

        #### CASE 2 ### Debate Started and user keeps refresh ### is_pause:False
        if is_refresh and (not is_pause):
            print("CASE2")
            current_epoch = int(time.time())
            if debateTime.get("lastPauseTime") and debateTime.get("lastStartedTime"):
                pause_duration = debateTime.get("lastStartedTime") - debateTime.get("lastPauseTime")
                debateTime["startedTime"] += pause_duration
        #######


        #### CASE 3 ### Debate Pause and User Keeps Refresh ##is_pause:True
        if is_refresh and is_pause:
            print("CASE3")
        #######
            current_epoch = debateTime.get("lastPauseTime")
        ####

        # Calculate total duration in seconds
        total_duration_seconds = total_hour * 3600 + total_minute * 60 + total_second
               
        # Set your start time
        elapsed_seconds = current_epoch - debateTime["startedTime"] 
        print(debateTime["startedTime"]," debate Start time")   
        # Calculate remaining time
      
        remaining_seconds = max(0, total_duration_seconds - elapsed_seconds)
        
        # Convert remaining seconds back to hours, minutes, seconds
        hour = remaining_seconds // 3600
        remaining_seconds %= 3600
        minute = remaining_seconds // 60
        second = remaining_seconds % 60
        
        # If remaining time becomes zero or negative, set all values to zero
        if hour <= 0 and minute <= 0 and second <= 0:
            hour = 0
            minute = 0
            second = 0
        
        # Debug output
        print(f"Total duration: {total_hour}h {total_minute}m {total_second}s")
        print(debateTime["startedTime"],"debate start time")
        print(debateTime["lastPauseTime"],"debate last time")
        print(f"current start {current_epoch}")
        print(f"Elapsed seconds: {elapsed_seconds}")
        print(f"Remaining seconds: {remaining_seconds}")
        print(f"Remaining time: {hour}h {minute}m {second}s")

        return hour, minute, second
