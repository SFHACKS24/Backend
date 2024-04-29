import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from db import db

from schemas import CustomQnsInfoSchema
from models import QnsInfoModel

blp=Blueprint("QuestionInfomation",__name__, description="Operations on questions")

@blp.route("/qnsInfo/<string:id>")
class Qns(MethodView):
    @blp.response(200,CustomQnsInfoSchema)
    def get(self,id):
        qns=QnsInfoModel.query.filter_by(id=id).first()
        if qns:
            return qns
        else:
            abort(404,message="Question not found")

@blp.route("/qnsInfo")
class QnsList(MethodView):
    @blp.arguments(CustomQnsInfoSchema)
    @blp.response(201,CustomQnsInfoSchema)
    def post(self,qns):
        new_qns_id=str(uuid.uuid4())
        qns["id"]=new_qns_id    
        qns= QnsInfoModel(**qns)
        try:
            db.session.add(qns)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(
                500,
                message=str(e)
            )
        return qns
    @blp.response(200,CustomQnsInfoSchema(many=True))
    def get(self):
        return QnsInfoModel.query.all()