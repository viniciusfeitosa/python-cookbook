from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Product(Base):
    __tablename__ = 'products'

    id = Column(String(250), primary_key=True)
    name = Column(String(250))
    price = Column(Float())
    stock = Column(Integer())
    created_at = Column(DateTime, default=datetime.utcnow)

    # class constructor
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.price = data.get('price')
        self.stock = data.get('stock')
