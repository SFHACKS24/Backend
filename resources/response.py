import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from db import db

from schemas import StructuredResponseSchema
from models import ResponseModel

blp=Blueprint("Responses",__name__, description="Operations on responses")

@blp.route("/responses/<string:userId>/<string:qnsId>")
class Qns(MethodView):
    @blp.response(200,StructuredResponseSchema(many=True))
    def get(self,userId,qnsId):
        response= ResponseModel.query.filter_by(userId=userId).first()
        if response:
            return response
        else:
            abort(404,message="Response not found") 
        


@blp.route("/response")
class QnsList(MethodView):
    @blp.arguments(StructuredResponseSchema)
    @blp.response(201,StructuredResponseSchema)
    def post(self,response):
        new_response_id=str(uuid.uuid4())
        response["id"]=new_response_id    
        # response["encoding"]=[]
        
        print(response)
        response= ResponseModel(**response)
        try:
            db.session.add(response)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(
                500,
                message=str(e)
            )
        return response
    @blp.response(200,StructuredResponseSchema(many=True))
    def get(self):
        return ResponseModel.query.all()