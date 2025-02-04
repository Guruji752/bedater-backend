from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.api_v1.deps.db_deps import Base
from app.models.general.ImageMaster import ImageMaster
from app.models.auth.UserMaster import UserMaster

class AvatarMaster(Base):
    __tablename__ = 'avatar_master'
    __table_args__ = {'schema': 'avatar'}

    id = Column(Integer, primary_key=True, server_default=text("nextval('avatar.avatar_master_id_seq'::regclass)"))
    user_id = Column(ForeignKey('auth.user_master.id'), nullable=False)
    gender = Column(String(100))
    skin_tone_id = Column(ForeignKey('general.image_master.id'), nullable=False)
    hair_colour_id = Column(ForeignKey('general.image_master.id'), nullable=False)
    dress_colour_id = Column(ForeignKey('general.image_master.id'), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    generated = Column(Integer, nullable=False, server_default=text("EXTRACT(epoch FROM now())"))

    dress_colour = relationship('ImageMaster', primaryjoin='AvatarMaster.dress_colour_id == ImageMaster.id')
    hair_colour = relationship('ImageMaster', primaryjoin='AvatarMaster.hair_colour_id == ImageMaster.id')
    skin_tone = relationship('ImageMaster', primaryjoin='AvatarMaster.skin_tone_id == ImageMaster.id')
    user = relationship('UserMaster') 
