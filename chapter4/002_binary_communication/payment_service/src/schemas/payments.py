from marshmallow import fields, Schema


class PaymentSchema(Schema):
    id = fields.Int(dump_only=True)
    consumer_id = fields.Str(dump_only=True)
    order_id = fields.Str(required=True)
    value_processed = fields.Float(dump_only=True)
