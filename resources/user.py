import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from db import users, db

from schemas import PlainUserSchema

blp=Blueprint("Users",__name__, description="Operations on users")

@blp.route("/users")
class Users(MethodView):
    @blp.response(200,PlainUserSchema(many=True))
    def get(self):
        return users
    
    @blp.arguments(PlainUserSchema)
    @blp.response(201,PlainUserSchema)
    def post(self,user):
        user["id"]=str(uuid.uuid4())
        users.append(user)
        return user
