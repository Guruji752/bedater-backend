from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.models.auth.UserMaster import UserMaster
from app.models.debate.DebateTypeMaster import DebateTypeMaster
from app.api_v1.deps.db_deps import Base


class DebateMaster(Base):
    __tablename__ = 'debate_master'
    __table_args__ = {'schema': 'debate'}

    id = Column(Integer, primary_key=True, server_default=text("nextval('debate.debate_master_id_seq'::regclass)"))
    debate_type_id = Column(ForeignKey('debate.debate_type_master.id'), nullable=False)
    # debate_status_type_id = Column(ForeignKey('debate.debate_status_type_master.id'), nullable=False)
    title = Column(String(500))
    room_id = Column(String(1000))
    hour = Column(String(10))
    minute = Column(String(10))
    seconds = Column(String(10))
    member_on_each_side = Column(Integer)
    participants_code = Column(String(100))
    audience_code = Column(String(100))
    generated = Column(Integer, nullable=False, server_default=text("EXTRACT(epoch FROM now())"))
    created_by = Column(ForeignKey('auth.user_master.id'), nullable=False)

    user_master = relationship('UserMaster')
    # debate_status_type = relationship('DebateStatusTypeMaster')
    debate_type = relationship('DebateTypeMaster')