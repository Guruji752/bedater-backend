from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.api_v1.deps.db_deps import Base


class UserSubscriptionDetail(Base):
    __tablename__ = 'user_subscription_details'
    __table_args__ = {'schema': 'users'}

    id = Column(Integer, primary_key=True, server_default=text("nextval('users.user_subscription_details_id_seq'::regclass)"))
    user_id = Column(ForeignKey('auth.user_master.id'), nullable=False)
    subscription_type_id = Column(ForeignKey('general.subscription_type.id'), nullable=False)
    payment_details_id = Column(ForeignKey('general.payment_details.id'), nullable=False)
    used_debated = Column(Integer)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    generated = Column(Integer, nullable=False, server_default=text("EXTRACT(epoch FROM now())"))

    payment_details = relationship('PaymentDetail')
    subscription_type = relationship('SubscriptionType')
    user = relationship('UserMaster')