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

from .models.payments import (
    Base,
    Payments,
)


class PaymentsServiceAPI:
    name = 'payments_service_api'
    payments_domain = RpcProxy('payments_domain')

    @http('GET', '/payments/<string:payment_id>')
    def get_payments(self, request, payment_id):
        respose_data = self.payments_domain.get_payment(payment_id)
        return 200, {'Content-Type': 'application/json'}, respose_data


class PaymentsHandler:
    name = 'payments_handler'
    payments_domain = RpcProxy('payments_domain')
    dispatcher = EventDispatcher()

    @event_handler('orders_domain', 'order_created')
    def do_payment(self, payload):
        data = json.loads(payload)
        try:
            data['payment_id'] = self.payments_domain.do_payment(payload)
            self.dispatcher('order_paid', json.dumps(data))
        except Exception as ex:
            self.dispatcher(
                'error',
                json.dumps({
                    'order_id': data.get('id'),
                    'error': str(ex),
                })
            )
            logging.error(str(ex))

    @event_handler('inventory_domain', 'inventory_error')
    def revert_payment(self, payment_id):
        try:
            self.payments_domain.delete_payment(payment_id)
        except Exception as ex:
            logging.error(str(ex))


class PaymentsDomain:
    name = 'payments_domain'
    db = DatabaseSession(Base)

    @rpc
    def do_payment(self, data):
        try:
            order = json.loads(data)
            payments = Payments({
                "id": str(uuid.uuid1()),
                "customer_id": order.get('customer_id'),
                "order_id": order.get('order_id'),
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
            raise Exception(str(e))

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
            raise Exception(str(e))

    @rpc
    def delete_payment(self, payment_id):
        try:
            payment = self.db.query(Payments).get(id)
            self.db.delete(payment)
            self.db.commit()
            return payment_id
        except Exception as e:
            self.db.rollback()
            logging.error(e)
