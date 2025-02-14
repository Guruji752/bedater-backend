from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.api_v1.deps.db_deps import Base


class VoteMaster(Base):
    __tablename__ = 'vote_master'
    __table_args__ = {'schema': 'vote'}

    id = Column(Integer, primary_key=True, server_default=text("nextval('vote.vote_master_id_seq'::regclass)"))
    debate_id = Column(ForeignKey('debate.debate_master.id'), nullable=False)
    topic_id = Column(ForeignKey('debate.topic_master.id'), nullable=False)
    team_id = Column(ForeignKey('debate.debate_participant_teams_details_master.id'), nullable=False)
    vote_type = Column(ForeignKey('vote.vote_type_master.id'), nullable=False)
    count = Column(Integer)
    generated = Column(Integer, nullable=False, server_default=text("EXTRACT(epoch FROM now())"))
    updated = Column(Integer, nullable=False, server_default=text("EXTRACT(epoch FROM now())"))

    debate = relationship('DebateMaster')
    team = relationship('DebateParticipantTeamsDetailsMaster')
    topic = relationship('TopicMaster')
    vote_type_master = relationship('VoteTypeMaster')