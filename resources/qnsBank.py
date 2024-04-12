import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from db import db,qnsBank

from schemas import QnsBankSchema

blp=Blueprint("Questions",__name__, description="Operations on question bank")

@blp.route("/qns/<int:id>")
class Qns(MethodView):
    @blp.response(200,QnsBankSchema)
    def get(self,id):
        for qns in qnsBank:
            if qns["id"]==id:
                return qns
        abort(404,message="Question not found")

@blp.route("/qns")
class QnsList(MethodView):
    @blp.arguments(QnsBankSchema)
    @blp.response(201,QnsBankSchema)
    def post(self,qns):
        new_qns_id=str(uuid.uuid4())
        qns["id"]=new_qns_id    
        qnsBank.append(qns)
        return qns