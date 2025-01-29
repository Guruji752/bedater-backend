from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.models.auth.UserMaster import UserMaster
from app.models.debate.DebateMaster import DebateMaster
from app.models.debate.TopicMaster import TopicMaster
from app.models.vote.VoteTypeMaster import VoteTypeMaster
from app.api_v1.deps.db_deps import Base

class AdvanceDebateDetailsMaster(Base):
    __tablename__ = 'advance_debate_details_master'
    __table_args__ = {'schema': 'debate'}

    id = Column(Integer, primary_key=True, server_default=text("nextval('debate.advance_debate_details_master_id_seq'::regclass)"))
    debate_id = Column(ForeignKey('debate.debate_master.id'), nullable=False)
    topic_id = Column(ForeignKey('debate.topic_master.id'), nullable=False)
    action_side = Column(String(100))
    voting_type = Column(ForeignKey('vote.vote_type_master.id'), nullable=False)
    voting_allowed = Column(Boolean, nullable=False, server_default=text("true"))
    generated = Column(Integer, nullable=False, server_default=text("EXTRACT(epoch FROM now())"))
    created_by = Column(ForeignKey('auth.user_master.id'), nullable=False)

    user_master = relationship('UserMaster')
    debate = relationship('DebateMaster')
    topic = relationship('TopicMaster')
    vote_type_master = relationship('VoteTypeMaster')