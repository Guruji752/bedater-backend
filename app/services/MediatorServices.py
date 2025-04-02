from app.models.debate.DebateMaster import DebateMaster
from app.models.debate.DebateTypeMaster import DebateTypeMaster
from app.models.debate.TopicMaster import TopicMaster
from app.models.debate.AdvanceDebateTopicTimeMaster import AdvanceDebateTopicTimeMaster
from app.services.RedisServices import RedisServices
from app.utils.enums import DebateType
from app.utils.common import get_virtual_id_fk

from app.models.debate.DebateParticipantTeamsDetailsMaster import DebateParticipantTeamsDetailsMaster
class MediatorServices:

    @staticmethod
    async def screenDetails(debate_id, virtual_id, db):
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
