from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.api_v1.deps.db_deps import Base

class DebateStatusMaster(Base):
    __tablename__ = 'debate_status_master'
    __table_args__ = {'schema': 'debate'}

    id = Column(Integer, primary_key=True, server_default=text("nextval('debate.debate_status_master_id_seq'::regclass)"))
    debate_id = Column(ForeignKey('debate.debate_master.id'), nullable=False)
    debate_status_type_id = Column(ForeignKey('debate.debate_status_type_master.id'), nullable=False)
    generated = Column(Integer, nullable=False, server_default=text("EXTRACT(epoch FROM now())"))
    last_updated = Column(Integer)
    created_by = Column(ForeignKey('auth.user_master.id'), nullable=False)

    user_master = relationship('UserMaster')
    debate = relationship('DebateMaster')
    debate_status_type = relationship('DebateStatusTypeMaster')