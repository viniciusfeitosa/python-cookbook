from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    BigInteger,
    DateTime,
    Index,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(length=200))
    email = Column(String)
    status = Column(String(length=50))
    created_at = Column(DateTime, default=datetime.utcnow)
    news_type = Column(String, default='famous')

    __table_args__ = Index('index', 'id', 'version'),
