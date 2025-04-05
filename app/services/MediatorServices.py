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

        def add_topics(topic_list,debate_id=debate_id,virtual_id=virtual_id,hour=0, minute=0, second=0):
            data = []
            for t in topic_list:
                is_complete = True if t.topic.topic in completed_topic else False
                is_selected = True if t.topic.topic in selected_topic else False
                is_pending = True if not (is_complete or is_selected) else False
                data.append({
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
            Topic.extend(add_topics(topics))
        elif debate_type == DebateType.ADVANCE.value:
            advance_topics = db.query(AdvanceDebateTopicTimeMaster).filter(
                AdvanceDebateTopicTimeMaster.debate_id == debate_id
            ).all()
            for t in advance_topics:
            	data = add_topics(advance_topics, hour=t.hour , minute=t.minute , second=t.seconds)

            Topic.extend(
                data
            )
        vk_fk = get_virtual_id_fk(virtual_id,db)

        team1,team2 = db.query(DebateParticipantTeamsDetailsMaster.team_name).filter(DebateParticipantTeamsDetailsMaster.debate_id == debate_id ,DebateParticipantTeamsDetailsMaster.virtual_id == vk_fk).all()
        
        return {"team1":team1[0],"team2":team2[0],"topic":Topic,"debate_title":debateTitle}

    @staticmethod
    async def mediatorDebateTimer(debate_id,virtual_id,is_pause,db):
        
        # virtual_id = get_virtual_id(debate_id,db)
        # import pdb;pdb.set_trace()
        debateTime= await RedisServices.debateStartTime(virtual_id)
        if not debateTime["status"]:
            return {"status":False}
        debate = db.query(DebateMaster).filter(DebateMaster.id == debate_id, DebateMaster.is_active == True).first()
        # Get the original total duration from debate object
        total_hour = int(debate.hour)
        total_minute = int(debate.minute)
        total_second = int(debate.seconds)
        # debateTime["startedTime"] = 1743860470
        if not debateTime["startedTime"]:
            # If startedTime is None, return the original duration
            return total_hour, total_minute, total_second

        # Calculate total duration in seconds
        total_duration_seconds = total_hour * 3600 + total_minute * 60 + total_second
          # Set your start time

        if debateTime["startedTime"]:
            # import pdb;pdb.set_trace()
            if is_pause:
                current_epoch = debateTime["lastPauseTime"]
            if not is_pause:
                current_epoch = int(time.time())

            # if debateTime["startedTime"]!=debateTime["lastPauseTime"]:
            #     current_epoch = debateTime["lastPauseTime"]
            # if debateTime["startedTime"] == debateTime["lastPauseTime"]:
            #     current_epoch = int(time.time())
            elapsed_seconds = current_epoch - debateTime["startedTime"]
            
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
            print(f"Elapsed seconds: {elapsed_seconds}")
            print(f"Remaining seconds: {remaining_seconds}")
            print(f"Remaining time: {hour}h {minute}m {second}s")

        return hour, minute, second
