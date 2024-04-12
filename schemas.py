from marshmallow import Schema, fields


class PlainUserSchema(Schema):
    id = fields.Str(dump_only=True)
    name=fields.Str(required=True)
    isMale=fields.Bool(required=True)
    age=fields.Int(required=True)
    occupation=fields.Str(required=True)
    location=fields.Str(required=True)
    budget=fields.Int(required=True)
    hasRoom=fields.Bool(required=True)


class QnsBankSchema(Schema):
    id = fields.Str(dump_only=True)
    question=fields.Str(required=True)
    type=fields.Int(required=True)

class StdResponsesSchema(Schema):
    id = fields.Str(dump_only=True)
    qnsId=fields.Str(required=True)
    userId=fields.Str(required=True)
    response=fields.Str(required=True)
    encoding=fields.List(fields.Int)

class CustomQnsSchema(Schema):
    id = fields.Str(dump_only=True)
    question=fields.Str(required=True)
    questionerId=fields.Str(required=True)

class CustomResponsesSchema(Schema):
    id = fields.Str(dump_only=True)
    questionerId=fields.Str(required=True)
    userId=fields.Str(required=True)
    response=fields.Str(required=True)
    encoding=fields.List(fields.Int)