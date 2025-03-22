from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from app.api_v1.deps.db_deps import Base

class DebateParticipantTeamsMaster(Base):
    __tablename__ = 'debate_participant_teams_master'
    __table_args__ = {'schema': 'debate'}

    id = Column(Integer, primary_key=True, server_default=text("nextval('debate.debate_participant_teams_master_id_seq'::regclass)"))
    debate_id = Column(ForeignKey('debate.debate_master.id'), nullable=False)
    team_side = Column(String(10))
    generated = Column(Integer, nullable=False, server_default=text("EXTRACT(epoch FROM now())"))
    created_by = Column(ForeignKey('auth.user_master.id'), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))

    user_master = relationship('UserMaster')
    debate = relationship('DebateMaster')