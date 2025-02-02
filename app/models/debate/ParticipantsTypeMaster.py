from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.models.auth.UserMaster import UserMaster
from app.api_v1.deps.db_deps import Base

class ParticipantsTypeMaster(Base):
    __tablename__ = 'participants_type_master'
    __table_args__ = {'schema': 'debate'}

    id = Column(Integer, primary_key=True, server_default=text("nextval('debate.participants_type_master_id_seq'::regclass)"))
    participant_type = Column(String(100))
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    generated = Column(Integer, nullable=False, server_default=text("EXTRACT(epoch FROM now())"))
    created_by = Column(ForeignKey('auth.user_master.id'), nullable=False)

    user_master = relationship('UserMaster')