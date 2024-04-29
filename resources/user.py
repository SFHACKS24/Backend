import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from db import db

from schemas import UserSchema
from models import UserModel

blp=Blueprint("Users",__name__, description="Operations on users")

@blp.route("/users")
class Users(MethodView):
    @blp.response(200,UserSchema(many=True))
    def get(self):
        return UserModel.query.all()
    
    @blp.arguments(UserSchema)
    @blp.response(201,UserSchema)
    def post(self,user):
        print("USER",user)
        user["id"]=str(uuid.uuid4())
        user= UserModel(**user)
        print(user)
        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(
                500,
                message=str(e)
            )
        return user
