from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.api_v1.deps.db_deps import Base
from app.models.auth.UserMaster import UserMaster

class ImageTypeMaster(Base):
    __tablename__ = 'image_type_master'
    __table_args__ = {'schema': 'general'}

    id = Column(Integer, primary_key=True, server_default=text("nextval('general.image_type_master_id_seq'::regclass)"))
    type = Column(String(100))
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    generated = Column(Integer, nullable=False, server_default=text("EXTRACT(epoch FROM now())"))
    created_by = Column(ForeignKey('auth.user_master.id'), nullable=False)

    user_master = relationship('UserMaster')