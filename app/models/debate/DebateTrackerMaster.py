from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.models.debate.DebateMaster import DebateMaster
from app.api_v1.deps.db_deps import Base


class DebateTrackerMaster(Base):
    __tablename__ = 'debate_tracker_master'
    __table_args__ = {'schema': 'debate'}

    id = Column(Integer, primary_key=True, server_default=text("nextval('debate.debate_tracker_master_id_seq'::regclass)"))
    debate_id = Column(ForeignKey('debate.debate_master.id'), nullable=False)
    virtual_id = Column(String(500))
    started_at = Column(Integer)
    is_active = Column(Boolean, nullable=False, server_default=text("false"))

    debate = relationship('DebateMaster')