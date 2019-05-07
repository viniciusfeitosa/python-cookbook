import json
import logging
import os
import uuid

from .protos.order_pb2 import OrderRequest
from .protos.order_pb2_grpc import OrderStub

from nameko.rpc import (
    rpc,
    RpcProxy,
)
from nameko.web.handlers import http
from nameko_sqlalchemy import DatabaseSession
from nameko_grpc.dependency_provider import GrpcProxy

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
    grpc = GrpcProxy('//{}'.format(os.getenv('ORDERS_URL')), OrderStub)

    @rpc
    def do_payment(self, data):
        try:
            order = self.grpc.unary_unary(
                OrderRequest(id=data.get('order_id'))
            )

            payments = Payments({
                "id": str(uuid.uuid1()),
                "customer_id": order.customerId,
                "order_id": data.get('order_id'),
                "value_processed": sum(
                    [
                        order.productPrice
                        for order in order.orderLines
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
