import json
import logging
import uuid

from nameko.events import (
    BROADCAST,
    event_handler,
    EventDispatcher,
)
from nameko.rpc import (
    rpc,
    RpcProxy,
)
from nameko.web.handlers import http
from nameko_sqlalchemy import DatabaseSession
from sqlalchemy.orm import joinedload

from .models.orders import (
    Base,
    Orders,
    OrderLines,
)
from .schemas.orders import OrderSchema


class OrdersServiceAPI:
    name = 'orders_service_api'
    orders_domain = RpcProxy('orders_domain')

    @http('POST', '/create_order')
    def create_orders(self, request):
        schema = OrderSchema(strict=True)
        try:
            data = schema.loads(request.get_data(as_text=True)).data
        except ValueError as ex:
            logging.info(
                'Data received: {}'.format(request.get_data(as_text=True))
            )
            logging.error(ex)
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
        response_data = self.orders_domain.get_order(order_id)
        if response_data:
            return 200, {'Content-Type': 'application/json'}, response_data
        return 404, \
            {'Content-Type': 'application/json'}, \
            json.dumps({'error': 'Not found {}'.format(order_id)})


class OrdersHandler:
    name = 'orders_handler'
    orders_domain = RpcProxy('orders_domain')

    @event_handler('payments_handler', 'error')
    @event_handler(
        'inventory_handler',
        'error',
        handler_type=BROADCAST,
        reliable_delivery=False,
    )
    def revert_orders(self, payload):
        logging.info('### Payload: {} ###'.format(payload))
        data = json.loads(payload)
        order_id = self.orders_domain.delete_order(data.get('order_id'))
        logging.info('Order {} deleted'.format(order_id))


class OrdersDomain:
    name = 'orders_domain'
    db = DatabaseSession(Base)
    dispatcher = EventDispatcher()

    @rpc
    def create_order(self, data):
        try:
            data['id'] = str(uuid.uuid1())
            logging.info('data: {}'.format(data))

            # updating order lines
            order_lines_updated = []
            for ol in data['order_lines']:
                ol['id'] = str(uuid.uuid1())
                ol['order_id'] = data['id']
                order_lines_updated.append(OrderLines(ol))
            data['order_lines'] = order_lines_updated
            logging.info('data updated: {}'.format(data))

            orders = Orders(data)
            self.db.add(orders)
            self.db.commit()
            self.dispatcher(
                'order_created',
                json.dumps(orders.to_dict())
            )
            return data.get('id')
        except Exception as e:
            self.db.rollback()
            logging.error(e)

    @rpc
    def get_order(self, id):
        try:
            order = self.db.query(Orders).options(
                joinedload(Orders.order_lines)).get(id)
            return json.dumps(order.to_dict()) if order else ''
        except Exception as e:
            logging.error(e)

    @rpc
    def delete_order(self, id):
        try:
            order = self.db.query(Orders).get(id)
            self.db.delete(order)
            self.db.commit()
            return id
        except Exception as e:
            self.db.rollback()
            logging.error(e)
