import json
import logging
import os
import uuid
import requests

from nameko.rpc import (
    rpc,
    RpcProxy,
)
from nameko.web.handlers import http
from nameko_sqlalchemy import DatabaseSession

from .models.payments import (
    Base,
    Payments,
)
from .schemas.payments import PaymentSchema


class PaymentsServiceAPI:
    name = 'payments_service_api'
    payments_domain = RpcProxy('payments_domain')

    @http('POST', '/do_payment')
    def do_payments(self, request):
        schema = PaymentSchema(strict=True)
        try:
            data = schema.loads(request.get_data(as_text=True)).data
        except ValueError as ex:
            logging.info(
                'Data received: {}'.format(request.get_data(as_text=True))
            )
            logging.error(ex)
            return 400, 'Invalid payload'

        try:
            payment_id = self.payments_domain.do_payment(data)
            return 201, {'Content-Type': 'application/json'}, json.dumps(
                {'payment_id': payment_id}
            )
        except Exception as e:
            logging.error(e)
            return 500, 'Internal Server Error'

    @http('GET', '/payments/<string:payment_id>')
    def get_payments(self, request, payment_id):
        respose_data = self.payments_domain.get_payment(payment_id)
        return 200, {'Content-Type': 'application/json'}, respose_data


class PaymentsDomain:
    name = 'payments_domain'
    db = DatabaseSession(Base)

    @rpc
    def do_payment(self, data):
        try:
            req = requests.get(
                'http://{}/orders/{}'.format(
                    os.getenv('ORDERS_URL'),
                    data.get('order_id'),
                )
            )
            order = req.json()

            payments = Payments({
                "id": str(uuid.uuid1()),
                "customer_id": order.get('customer_id'),
                "order_id": data.get('order_id'),
                "value_processed": sum(
                    [
                        ol['product_price']
                        for ol in order.get('order_lines')
                    ]
                )
            })
            self.db.add(payments)
            self.db.commit()
            return payments.id
        except Exception as e:
            self.db.rollback()
            logging.error(e)

    @rpc
    def get_payment(self, id):
        try:
            payment = self.db.query(Payments).get(id)
            payment_response = {
                "id": payment.id,
                "customer_id": payment.customer_id,
                "order_id": payment.order_id,
                "value_processed": payment.value_processed,
            }
            return json.dumps(payment_response)
        except Exception as e:
            self.db.rollback()
            logging.error(e)
