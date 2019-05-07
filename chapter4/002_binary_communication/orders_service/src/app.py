import json
import logging
import uuid

from .protos.order_pb2 import OrderResponse, OrderLine
from .protos.order_pb2_grpc import OrderStub

from nameko.rpc import (
    rpc,
    RpcProxy,
)
from nameko.web.handlers import http
from nameko_sqlalchemy import DatabaseSession
from nameko_grpc.entrypoint import Grpc
from sqlalchemy.orm import joinedload

from .models.orders import (
    Base,
    Orders,
    OrderLines,
)
from .schemas.orders import OrderSchema


grpc = Grpc.implementing(OrderStub)


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

    @grpc
    def GetOrderByID(self, request, context):
        response_data = self.orders_domain.get_order(request.orderId)
        return OrderResponse(
            id=response_data.get('id'),
            customerId=response_data.get('customer_id'),
            orderLines=[
                OrderLine(
                    id=ol.get('id'),
                    orderId=ol.get('order_id'),
                    productId=ol.get('product_id'),
                    productPrice=ol.get('product_price'),
                )
                for ol in response_data.get('order_lines')
            ],
        )


class OrdersDomain:
    name = 'orders_domain'
    db = DatabaseSession(Base)

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
            return data.get('id')
        except Exception as e:
            self.db.rollback()
            logging.error(e)

    @rpc
    def get_order(self, id):
        try:
            order = self.db.query(Orders).options(
                joinedload(Orders.order_lines)).get(id)
            order_response = {
                "id": order.id,
                "customer_id": order.customer_id,
                "order_lines": [
                    {
                        "id": ol.id,
                        "order_id": ol.order_id,
                        "product_id": ol.product_id,
                        "product_price": ol.product_price,
                    }
                    for ol in order.order_lines
                ]
            }
            return json.dumps(order_response)
        except Exception as e:
            self.db.rollback()
            logging.error(e)
