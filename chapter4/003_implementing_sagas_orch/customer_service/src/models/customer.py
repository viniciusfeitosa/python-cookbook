from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    String,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Customers(Base):
    __tablename__ = 'customers'

    id = Column(String(250), primary_key=True)
    customer_id = Column(String(250))
    customer_lines = relationship('CustomerLines')
    created_at = Column(DateTime, default=datetime.utcnow)

    # class constructor
    def __init__(self, data):
        self.id = data.get('id')
        self.customer_id = data.get('customer_id')
        self.customer_lines = data.get('order_lines')


class CustomerLines(Base):
    __tablename__ = 'customer_lines'

    id = Column(String(250), primary_key=True)
    customer_id = Column(String(250), ForeignKey('orders.id'))
    product_id = Column(String(250))
    product_price = Column(Float)

    # class constructor
    def __init__(self, data):
        self.id = data.get('id')
        self.customer_id = data.get('order_id')
        self.product_id = data.get('product_id')
        self.product_price = data.get('product_price')
