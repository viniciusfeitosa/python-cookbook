import os
from datetime import datetime

from mongoengine import (
    BooleanField,
    connect,
    Document,
    DateTimeField,
    ListField,
    StringField,
)

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    String,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class NewsCommandModel(Base):
    __tablename__ = 'news'

    id = Column(String(250), primary_key=True)
    author = Column(String(150))
    title = Column(String(150), nullable=False)
    content = Column(String(), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=False)
    tags = Column(postgresql.ARRAY(String))

    # class constructor
    def __init__(self, data):
        self.id = data.get('id')
        self.author = data.get('author')
        self.title = data.get('title')
        self.content = data.get('content')
        self.is_active = data.get('is_active')
        self.tags = data.get('tags')


connect('news', host=os.environ.get('QUERY_DATABASE_URL'))


class NewsQueryModel(Document):
    id = StringField(primary_key=True)
    author = StringField(required=True, max_length=50)
    title = StringField(required=True, max_length=200)
    content = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    is_active = BooleanField(default=False)
    tags = ListField(StringField(max_length=50))
