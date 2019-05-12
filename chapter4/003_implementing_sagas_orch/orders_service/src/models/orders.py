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


class Orders(Base):
    __tablename__ = 'orders'

    id = Column(String(250), primary_key=True)
    customer_id = Column(String(250))
    order_lines = relationship('OrderLines')
    created_at = Column(DateTime, default=datetime.utcnow)

    # class constructor
    def __init__(self, data):
        self.id = data.get('id')
        self.customer_id = data.get('customer_id')
        self.order_lines = data.get('order_lines')

    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "order_lines": [
                {
                    "id": ol.id,
                    "order_id": ol.order_id,
                    "product_id": ol.product_id,
                    "product_price": ol.product_price,
                }
                for ol in self.order_lines
            ]
        }


class OrderLines(Base):
    __tablename__ = 'order_lines'

    id = Column(String(250), primary_key=True)
    order_id = Column(String(250), ForeignKey('orders.id'))
    product_id = Column(String(250))
    product_price = Column(Float)

    # class constructor
    def __init__(self, data):
        self.id = data.get('id')
        self.order_id = data.get('order_id')
        self.product_id = data.get('product_id')
        self.product_price = data.get('product_price')
