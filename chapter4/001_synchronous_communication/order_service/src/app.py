import json
import logging
import uuid

from nameko.rpc import (
    rpc,
    RpcProxy,
)
from nameko.web.handlers import http
from nameko_sqlalchemy import DatabaseSession

from .models.orders import (
    Base,
    Orders,
)
from .schemas.orders import OrdersSchema


class OrdersServiceAPI:
    name = 'orders_service_api'
    orders_domain = RpcProxy('orders_domain')

    @http('POST', '/create_order')
    def create_orders(self, request):
        schema = OrdersSchema(strict=True)
        try:
            data = schema.loads(request.get_data(as_text=True)).data
        except ValueError:
            return 400, 'Invalid payload'

        try:
            order_id = self.orders_domain.create_order(data)
            return 201, {'Content-Type': 'application/json'}, json.dumps(
                {'order_id': order_id}
            )
        except Exception as e:
            logging.error(e)
            return 500, 'Internal Server Error'

    @http('GET', '/orders/<string:order_id>')
    def get_orders(self, request, order_id):
        respose_data = self.orders_domain.get_order(order_id)
        return 200, {'Content-Type': 'application/json'}, respose_data


class OrdersDomain:
    name = 'orders_domain'
    db = DatabaseSession(Base)

    @rpc
    def create_order(self, data):
        try:
            data['id'] = str(uuid.uuid1())
            orders = Orders(data)
            self.db.add(orders)
            self.db.commit()
            return data.get('id')
        except Exception as e:
            self.db.rollback()
            logging.error(e)

    @rpc
    def get_order(self, id):
        try:
            order = self.db.query(Orders).get(id)
            return json.dumps(order.to_dict())
        except Exception as e:
            self.db.rollback()
            logging.error(e)
