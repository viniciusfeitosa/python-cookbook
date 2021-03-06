from marshmallow import fields, Schema


class NewsSchema(Schema):
    id = fields.Int(dump_only=True)
    author = fields.Str(required=True)
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    is_active = fields.Bool(required=True)
    tags = fields.List(fields.Str, required=True)
