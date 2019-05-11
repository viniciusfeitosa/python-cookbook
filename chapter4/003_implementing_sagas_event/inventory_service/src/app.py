import json
import logging
import uuid

from nameko.events import (
    event_handler,
    EventDispatcher
)
from nameko.rpc import (
    rpc,
    RpcProxy,
)
from nameko.web.handlers import http
from nameko_sqlalchemy import DatabaseSession

from .models.inventory import (
    Base,
    Product,
)
from .schemas.inventory import (
    ProductSchema,
    ProductStockSchema,
)


class InventoryServiceAPI:
    name = 'inventory_service_api'
    inventory_domain = RpcProxy('inventory_domain')

    @http('POST', '/add_product')
    def add_product(self, request):
        schema = ProductSchema(strict=True)
        try:
            data = schema.loads(request.get_data(as_text=True)).data
        except ValueError as ex:
            logging.info(
                'Data received: {}'.format(request.get_data(as_text=True))
            )
            logging.error(ex)
            return 400, 'Invalid payload'

        try:
            product_id = self.inventory_domain.add_product(data)
            return 201, {'Content-Type': 'application/json'}, json.dumps(
                {'product_id': product_id}
            )
        except Exception as e:
            logging.error(e)
            return 500, 'Internal Server Error'

    @http('PUT', 'update_stock/product/<string:product_id>')
    def update_product_stock(self, request, product_id):
        schema = ProductStockSchema(strict=True)
        try:
            data = schema.loads(request.get_data(as_text=True)).data
            if data.get('stock') < 0:
                raise ValueError('Stock can not be a negative value')
        except ValueError as ex:
            logging.info(
                'Data received: {}'.format(request.get_data(as_text=True))
            )
            logging.error(ex)
            return 400, 'Invalid payload'

        try:
            self.inventory_domain.update_product_stock(product_id, data)
        except Exception as e:
            return 500, str(e)

    @http('GET', '/inventory/product/<string:product_id>')
    def get_products(self, request, product_id):
        respose_data = self.inventory_domain.get_product(product_id)
        return 200, {'Content-Type': 'application/json'}, respose_data


class InventoryHandler:
    name = 'inventory_handler'
    inventory_domain = RpcProxy('inventory_domain')
    dispatcher = EventDispatcher()

    @event_handler('payments_domain', 'order_paid')
    def decrease_stock(self, payload):
        try:
            data = json.loads(payload)
            self.inventory_domain.decrease_stock(data)
        except Exception as ex:
            self.dispatcher(
                'error',
                json.dumps({
                    'order_id': data.get('id'),
                    'error': str(ex),
                })
            )
            logging.error(str(ex))


class InventoryDomain:
    name = 'inventory_domain'
    db = DatabaseSession(Base)

    @rpc
    def add_product(self, data):
        try:
            data['id'] = str(uuid.uuid1())
            logging.info('data: {}'.format(data))

            product = Product(data)
            self.db.add(product)
            self.db.commit()
            return data.get('id')
        except Exception as e:
            self.db.rollback()
            logging.error(e)

    @rpc
    def decrease_stock(self, data):
        try:
            for ol in data.get('order_lines'):
                product = self.db.query(Product).get(ol.get('product_id'))
                quantity = ol.get('product_price') / product.product_price
                product.stock = product.stock - int(quantity)
                self.db.add(product)
                self.db.commit()
            return 'ok'
        except Exception as e:
            self.db.rollback()
            logging.error(e)

    @rpc
    def get_product(self, id):
        try:
            product = self.db.query(Product).get(id)
            product_response = {
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'stock': product.stock,
                'created_at': product.created_at,
            }
            return json.dumps(product_response)
        except Exception as e:
            self.db.rollback()
            logging.error(e)
