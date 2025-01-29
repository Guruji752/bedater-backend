from sqlalchemy import Boolean, Column, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base
from app.api_v1.deps.db_deps import Base

class UserMaster(Base):
    __tablename__ = 'user_master'
    __table_args__ = {'schema': 'auth'}

    id = Column(Integer, primary_key=True, server_default=text("nextval('auth.user_master_id_seq'::regclass)"))
    username = Column(String(500), nullable=False, unique=True)
    email = Column(String(500))
    name = Column(String(100))
    gender = Column(String(20))
    phone_no = Column(String(100))
    profile_exist = Column(Boolean, nullable=False, server_default=text("false"))
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    generated = Column(Integer, nullable=False, server_default=text("EXTRACT(epoch FROM now())"))