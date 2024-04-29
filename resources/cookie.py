import uuid
from flask import jsonify, request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from db import db

from schemas import CookieSchema
from models import CookieModel

blp=Blueprint("Cookie",__name__, description="Operations on cookies")

@blp.route("/cookies")
class NewCookie(MethodView):
    @blp.response(200,CookieSchema(many=True))
    def get(self):
        return CookieSchema.query.all()
    
    @blp.arguments(CookieSchema)
    @blp.response(201,CookieSchema)
    def post(self,cookie):
        cookie["id"]=str(uuid.uuid4())
        cookieObj= CookieModel(**cookie)
        try:
            # currentCookies= CookieModel.query.filter_by(userId=cookie["userId"]).all()
            # for c in currentCookies:
            #     db.session.delete(c)
            db.session.add(cookieObj)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(
                500,
                message=str(e)
            )
        return cookieObj
@blp.route("/cookies/<string:cookieId>")
class Cookie(MethodView):
    @blp.response(200,CookieSchema)
    def get(self,cookieId):
        cookie= CookieModel.query.filter_by(id=cookieId).first()
        if cookie:
            return cookie
        else:
            abort(404,message="Cookie not found")

    @blp.arguments(CookieSchema)
    @blp.response(201,CookieSchema)
    def put(self,cookieId,cookie):
        cookieObj= CookieModel.query.filter_by(id=cookieId).first()
        if cookieObj:
            for key in cookie:
                setattr(cookieObj,key,cookie[key])
            db.session.commit()
            return cookieObj
        else:
            abort(404,message="Cookie not found")

    def delete(self,cookieId):
        cookieObj= CookieModel.query.filter_by(id=cookieId).first()
        if cookieObj:
            db.session.delete(cookieObj)
            db.session.commit()
            return "Cookie deleted"
        else:
            abort(404,message="Cookie not found")
    
@blp.route("/cookiesProgress/<string:cookieId>")
class cookieProgress(MethodView):
    def get(self,cookieId):
        cookie= CookieModel.query.filter_by(id=cookieId).first()
        if cookie:
            return jsonify(cookie.currentProgress)
        else:
            abort(404,message="Cookie not found")

    def put(self,cookieId):
        cookieObj= CookieModel.query.filter_by(id=cookieId).first()
        if cookieObj:
            cookieObj.currentProgress+=1
            print("current progress", cookieObj.currentProgress)
            if cookieObj.currentProgress>=10: #match number of qns
                db.session.commit()
                return "1"
            db.session.commit()
            return "0"
        else:
            abort(404,message="Cookie not found")

@blp.route("/cookiesRecommend/<string:cookieId>")
class cookieRecommendation(MethodView):
    def get(self,cookieId):
        cookie= CookieModel.query.filter_by(id=cookieId).first()
        if cookie:
            return jsonify(cookie.hasDirectRecommendation)
        else:
            abort(404,message="Cookie not found")

    def put(self,cookieId):
        cookieObj= CookieModel.query.filter_by(id=cookieId).first()
        if cookieObj:
            cookieObj.hasDirectRecommendation=True
            db.session.commit()
            return cookieObj
        else:
            abort(404,message="Cookie not found")
@blp.route("/cookiesUser/<string:cookieId>")
class cookieUser(MethodView):
    def get(self,cookieId):
        cookie= CookieModel.query.filter_by(id=cookieId).first()
        if cookie:
            return jsonify(cookie.userId)
        else:
            abort(404,message="Cookie not found")
    def post(self,cookieId):
        cookieObj= CookieModel.query.filter_by(id=cookieId).first()
        if cookieObj:
            cookieObj.isComplete=True
            db.session.commit()
            return cookieObj
        else:
            abort(404,message="Cookie not found")