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

class QnsInfoSchema(Schema):
    id = fields.Str(dump_only=True)
    question=fields.Str(required=True)
    type=fields.Int(required=True)

class CustomQnsInfoSchema(QnsInfoSchema):
    questionerId=fields.Str(required=False)

class ResponseSchema(Schema):
    id = fields.Str(dump_only=True)
    response=fields.Str(required=True)
    userId=fields.Str(required=True)
    qnsId=fields.Str(required=True)

class StructuredResponseSchema(ResponseSchema):
    encoding=fields.Raw(required=False)

class UserSchema(PlainUserSchema):
    userResponses=fields.List(fields.Nested(ResponseSchema), required=False)
    posedQns=fields.Nested(CustomQnsInfoSchema, required=False)

class CookieSchema(Schema):
    id=fields.Str(dump_only=True)
    userId= fields.Str(required=True)
    currentProgress= fields.Int(required=True)
    isCompleted=fields.Bool(required=True)
    hasDirectRecommendation=fields.Bool(required=True)