from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from app.models.auth.UserMaster import UserMaster
from app.models.debate.DebateMaster import DebateMaster
from app.api_v1.deps.db_deps import Base


class TopicMaster(Base):
    __tablename__ = 'topic_master'
    __table_args__ = {'schema': 'debate'}

    id = Column(Integer, primary_key=True, server_default=text("nextval('debate.topic_master_id_seq'::regclass)"))
    debate_id = Column(ForeignKey('debate.debate_master.id'), nullable=False)
    topic = Column(String(500))
    generated = Column(Integer, nullable=False, server_default=text("EXTRACT(epoch FROM now())"))
    created_by = Column(ForeignKey('auth.user_master.id'), nullable=False)

    user_master = relationship('UserMaster')
    debate = relationship('DebateMaster')