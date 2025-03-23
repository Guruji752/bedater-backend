from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from app.api_v1.deps.db_deps import Base
from app.models.debate.DebateParticipantMaster import DebateParticipantMaster
from app.models.debate.DebateParticipantTeamsDetailsMaster import DebateParticipantTeamsDetailsMaster
from app.models.debate.DebateMaster import DebateMaster
class DebateParticipantDetail(Base):
    __tablename__ = 'debate_participant_details'
    __table_args__ = {'schema': 'debate'}

    id = Column(Integer, primary_key=True, server_default=text("nextval('debate.debate_participant_details_id_seq'::regclass)"))
    participant_id = Column(ForeignKey('debate.debate_participant_master.id'), nullable=False)
    joined_team = Column(ForeignKey('debate.debate_participant_teams_master.id'), nullable=False)
    debate_id = Column(ForeignKey('debate.debate_master.id'), nullable=False)
    generated = Column(Integer, nullable=False, server_default=text("EXTRACT(epoch FROM now())"))
    is_active = Column(Boolean, nullable=False, server_default=text("true"))

    debate = relationship('DebateMaster')
    debate_participant_teams_master = relationship('DebateParticipantTeamsMaster')
    participant = relationship('DebateParticipantMaster')