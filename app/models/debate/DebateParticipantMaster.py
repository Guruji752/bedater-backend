from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from app.api_v1.deps.db_deps import Base
from app.models.auth.UserMaster import UserMaster
from app.models.debate.ParticipantsTypeMaster import ParticipantsTypeMaster

class DebateParticipantMaster(Base):
    __tablename__ = 'debate_participant_master'
    __table_args__ = {'schema': 'debate'}

    id = Column(Integer, primary_key=True, server_default=text("nextval('debate.debate_participant_master_id_seq'::regclass)"))
    debate_id = Column(ForeignKey('debate.debate_master.id'), nullable=False)
    user_id = Column(ForeignKey('auth.user_master.id'), nullable=False)
    participant_type_id = Column(ForeignKey('debate.participants_type_master.id'), nullable=False)
    is_locked = Column(Boolean, nullable=False, server_default=text("false"))
    generated = Column(Integer, nullable=False, server_default=text("EXTRACT(epoch FROM now())"))
    is_active = Column(Integer, nullable=False, server_default=text("EXTRACT(epoch FROM now())"))

    debate = relationship('DebateMaster')
    participant_type = relationship('ParticipantsTypeMaster')
    user = relationship('UserMaster')