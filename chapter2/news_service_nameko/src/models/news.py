import datetime
import enum

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    String,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class PlanEnum(enum.Enum):
    F = 'free'
    S = 'subscribers'


class NewsModel(Base):
    __tablename__ = 'news'

    id = Column(BigInteger, primary_key=True)
    author = Column(BigInteger)
    title = Column(String(150), nullable=False)
    content = Column(String(), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=False)
    tags = Column(postgresql.ARRAY(String))

    # class constructor
    def __init__(self, data):
        self.author = data.get('author')
        self.title = data.get('title')
        self.content = data.get('content')
        self.is_active = data.get('is_active')
        self.tags = data.get('tags')
