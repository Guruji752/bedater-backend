from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.models.auth.UserMaster import UserMaster
from app.models.debate.DebateMaster import DebateMaster
from app.api_v1.deps.db_deps import Base


class CounterStatementsMaster(Base):
    __tablename__ = 'counter_statements_master'
    __table_args__ = {'schema': 'debate'}

    id = Column(Integer, primary_key=True, server_default=text("nextval('debate.counter_statements_master_id_seq'::regclass)"))
    debate_id = Column(ForeignKey('debate.debate_master.id'), nullable=False)
    counters = Column(Integer)
    seconds = Column(String(10))
    generated = Column(Integer, nullable=False, server_default=text("EXTRACT(epoch FROM now())"))
    created_by = Column(ForeignKey('auth.user_master.id'), nullable=False)

    user_master = relationship('UserMaster')
    debate = relationship('DebateMaster')