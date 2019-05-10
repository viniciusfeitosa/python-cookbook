from marshmallow import fields, Schema


class ProductSchema(Schema):
    id = fields.String(dump_only=True)
    name = fields.Str(dump_only=True)
    price = fields.Float(required=True)
    stock = fields.Int(required=True)


class ProductStockSchema(Schema):
    id = fields.String(dump_only=True)
    stock = fields.Int(required=True)
