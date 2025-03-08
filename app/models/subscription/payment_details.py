from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.api_v1.deps.db_deps import Base


class PaymentDetail(Base):
    __tablename__ = 'payment_details'
    __table_args__ = {'schema': 'general'}

    id = Column(Integer, primary_key=True, server_default=text("nextval('general.payment_details_id_seq'::regclass)"))
    transiction_id = Column(String(200))
    subscription_type_id = Column(ForeignKey('general.subscription_type.id'), nullable=False)
    generated = Column(Integer, nullable=False, server_default=text("EXTRACT(epoch FROM now())"))

    subscription_type = relationship('SubscriptionType')