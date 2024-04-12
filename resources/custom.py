import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from db import db,customQns,customResponses

from schemas import CustomQnsSchema,CustomResponsesSchema

blp=Blueprint("Custom Qns + Response",__name__, description="Operations on cusotm qns + Response")

@blp.route("/customResponses/<string:questionerId>/<string:userId>")
class response(MethodView):
    @blp.response(200,CustomResponsesSchema(many=True))
    def get(self,questionerId,userId):
        if userId=="-1":
            return [response for response in customResponses if response["questionerId"]==questionerId]
        return [response for response in customResponses if response["userId"]==userId and response["questionerId"]==questionerId]


@blp.route("/customResponses")
class responseList(MethodView):
    @blp.arguments(CustomResponsesSchema)
    @blp.response(201,CustomResponsesSchema)
    def post(self,response):
        new_response_id=str(uuid.uuid4())
        response["id"]=new_response_id    
        response["encoding"]=[]
        customResponses.append(response)
        return response
    
@blp.route("/customQns/<string:questionerId>")
class Qns(MethodView):
    @blp.response(200,CustomQnsSchema(many=True))
    def get(self,questionerId):
        if questionerId=="-1":
            return customQns
        return [qns for qns in customQns if qns["questionerId"]==questionerId]
    
    @blp.arguments(CustomQnsSchema)
    @blp.response(201,CustomQnsSchema)
    def post(self,qns, questionerId):
        new_qns_id=str(uuid.uuid4())
        qns["id"]=new_qns_id    
        customQns.append(qns)
        return qns