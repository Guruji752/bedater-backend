from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.api_v1.deps.db_deps import Base

class DebateStatusTypeMaster(Base):
    __tablename__ = 'debate_status_type_master'
    __table_args__ = {'schema': 'debate'}

    id = Column(Integer, primary_key=True, server_default=text("nextval('debate.debate_status_type_master_id_seq'::regclass)"))
    type = Column(String(100))
    is_active = Column(Boolean, nullable=False, server_default=text("true"))