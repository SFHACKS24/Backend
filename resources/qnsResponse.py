import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from db import db,stdResponses

from schemas import StdResponsesSchema

blp=Blueprint("Responses to Question Bank",__name__, description="Operations on question bank")

@blp.route("/userResponses/<string:userId>/<string:qnsId>")
class Qns(MethodView):
    @blp.response(200,StdResponsesSchema(many=True))
    def get(self,userId,qnsId):
        if qnsId=="-1":
            return [response for response in stdResponses if response["userId"]==userId]
        return [response for response in stdResponses if response["userId"]==userId and response["qnsId"]==qnsId]


@blp.route("/userResponses")
class QnsList(MethodView):
    @blp.arguments(StdResponsesSchema)
    @blp.response(201,StdResponsesSchema)
    def post(self,response):
        new_response_id=str(uuid.uuid4())
        response["id"]=new_response_id    
        response["encoding"]=[]
        stdResponses.append(response)
        return response