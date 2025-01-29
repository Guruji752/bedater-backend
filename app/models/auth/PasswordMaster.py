from sqlalchemy import Boolean, Column, Integer, String, text,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from app.api_v1.deps.db_deps import Base
from app.models.auth.UserMaster import UserMaster
from sqlalchemy.orm import relationship


class PasswordMaster(Base):
    __tablename__ = 'password_master'
    __table_args__ = {'schema': 'auth'}

    id = Column(Integer, primary_key=True, server_default=text("nextval('auth.password_master_id_seq'::regclass)"))
    user_id = Column(ForeignKey('auth.user_master.id'), nullable=False)
    password = Column(String(500), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    generated = Column(Integer, nullable=False, server_default=text("EXTRACT(epoch FROM now())"))
    user = relationship('UserMaster')