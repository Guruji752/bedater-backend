from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, text,Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.api_v1.deps.db_deps import Base


class SubscriptionType(Base):
    __tablename__ = 'subscription_type'
    __table_args__ = {'schema': 'general'}

    id = Column(Integer, primary_key=True, server_default=text("nextval('general.subscription_type_id_seq'::regclass)"))
    plan_name = Column(String(300))
    amount = Column(Numeric(10, 2), nullable=False, server_default=text("0.00"))
    debate_type = Column(ForeignKey('debate.debate_type_master.id'), nullable=False)
    allowed_debate = Column(Integer)
    created_by = Column(ForeignKey('auth.user_master.id'), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    generated = Column(Integer, nullable=False, server_default=text("EXTRACT(epoch FROM now())"))

    user_master = relationship('UserMaster')
    debate_type_master = relationship('DebateTypeMaster')