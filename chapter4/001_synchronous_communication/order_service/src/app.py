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
    # OrderLines,
)
from .schemas.orders import OrdersSchema


class OrdersServiceAPI:
    name = 'orders_service_api'
    query_stack = RpcProxy('query_stack')
    command_stack = RpcProxy('command_stack')

    @http('POST', '/create_orders')
    def create_orders(self, request):
        schema = OrdersSchema(strict=True)
        try:
            data = schema.loads(request.get_data(as_text=True)).data
        except ValueError:
            return 400, 'Invalid payload'

        try:
            orders_id = self.command_stack.orders_domain(data)
            localtion = {
                'Location': 'http://localhost:5000/orders/{}'.format(orders_id)
            }
            return 202, localtion, 'ACCEPTED'
        except Exception as e:
            logging.error(e)
            return 500, 'Internal Server Error'

    @http('GET', '/orders/list/page/<int:page>/limit/<int:limit>')
    def list_orders(self, request, page, limit):
        respose_data = self.query_stack.list_orders(page, limit)
        return 200, {'Content-Type': 'application/json'}, respose_data

    @http('GET', '/orders/<string:orders_id>')
    def get_orders(self, request, orders_id):
        respose_data = self.query_stack.get_orders(orders_id)
        return 200, {'Content-Type': 'application/json'}, respose_data


class CommandOrdersService:
    db = DatabaseSession(Base)

    @rpc
    def orders_domain(self, data):
        try:
            data['id'] = str(uuid.uuid1())
            orders = Orders(data)
            self.db.add(orders)
            self.db.commit()
            self.dispatcher('orders_created', data)
            return data.get('id')
        except Exception as e:
            self.db.rollback()
            logging.error(e)
