import json
import logging
import uuid

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
from .schemas.inventory import ProductSchema


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

    @http('GET', '/inventory/product/<string:product_id>')
    def get_orders(self, request, product_id):
        respose_data = self.inventory_domain.get_product(product_id)
        return 200, {'Content-Type': 'application/json'}, respose_data


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
