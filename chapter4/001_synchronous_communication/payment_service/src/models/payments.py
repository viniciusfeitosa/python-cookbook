from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    String,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Payments(Base):
    __tablename__ = 'payments'

    id = Column(String(250), primary_key=True)
    customer_id = Column(String(250))
    order_id = Column(String(250))
    value_processed = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    # class constructor
    def __init__(self, data):
        self.id = data.get('id')
        self.customer_id = data.get('customer_id')
        self.order_id = data.get('order_id')
        self.value_processed = data.get('value_processed')
