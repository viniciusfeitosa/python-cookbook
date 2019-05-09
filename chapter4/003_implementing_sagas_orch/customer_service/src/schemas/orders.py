from marshmallow import fields, Schema


class OrderLineSchema(Schema):
    id = fields.Int(dump_only=True)
    order_id = fields.Str(dump_only=True)
    product_id = fields.Str(required=True)
    product_price = fields.Float(required=True)


class OrderSchema(Schema):
    id = fields.Str(dump_only=True)
    customer_id = fields.Str(required=True)
    order_lines = fields.List(fields.Nested(OrderLineSchema), required=True)
    created_at = fields.DateTime(dump_only=True)
