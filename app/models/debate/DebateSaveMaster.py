from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.models.debate.DebateStatusTypeMaster import DebateStatusTypeMaster
from app.models.debate.DebateMaster import DebateMaster
from app.models.auth.UserMaster import UserMaster
from app.api_v1.deps.db_deps import Base


class DebateSaveMaster(Base):
    __tablename__ = 'debate_save_master'
    __table_args__ = {'schema': 'debate'}

    id = Column(Integer, primary_key=True, server_default=text("nextval('debate.debate_save_master_id_seq'::regclass)"))
    debate_id = Column(ForeignKey('debate.debate_master.id'), nullable=False)
    debate_status_type_id = Column(ForeignKey('debate.debate_status_type_master.id'), nullable=False)
    created_by = Column(ForeignKey('auth.user_master.id'), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))

    user_master = relationship('UserMaster')
    debate = relationship('DebateMaster')
    debate_status_type = relationship('DebateStatusTypeMaster')