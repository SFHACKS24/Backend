import json
import uuid
from flask import jsonify, request, make_response
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from db import db
import requests
from llm import fastEmbedding
from schemas import UserSchema
from models import QnsInfoModel

questionMapping=["2ac53c24-cca9-4c86-be9e-8684b1065853","3dd5590a-d2a2-4553-842c-29fb9a5e394c","eab70460-d917-4a1c-9591-b38dfd749ff1","2c2642b7-fd6b-4a9b-bc86-a41a346e1507","d2104edb-12f4-481c-94b8-12b9bc059786","2eb0fd4a-3bdd-4e57-ab65-e0eb967d2aa0","a96e565b-e3cf-4636-a440-79de1a62bd57","bae27097-1d06-49c4-b18e-82246c7a6b83","4c0e8bdd-b26c-462a-b177-13721086a35f","b1499254-4e7c-47c6-acc3-6d32d50af99e"]

blp=Blueprint("Backend Functionalities",__name__, description="Backend Operations")
DB_URL="http://localhost:5000"

@blp.route("/initUser")
class InitUser(MethodView):
    def get(self):
        userUrl=f"{DB_URL}/users"
        body = {
            "name":request.json["name"],
            "isMale":request.json["isMale"],
            "age":request.json["age"],
            "occupation":request.json["occupation"],
            "location":request.json["location"],
            "budget":request.json["budget"],
            "hasRoom":request.json["hasRoom"],
        }
        user= requests.post(userUrl, json=body).json()
        cookieUrl=f"{DB_URL}/cookies"
        body = {
            "userId":user["id"],
            "currentProgress":0,
            "hasDirectRecommendation":False,
            "isCompleted":False
        }
        cookie= requests.post(cookieUrl, json=body).json()
        resp= make_response("set cookie")
        resp.set_cookie("GreenFlags",cookie["id"])
        return resp #must return this to set cookie

@blp.route("/getQns")
class GetQns(MethodView):
    def get(self):
        cookieId= request.cookies.get("GreenFlags")
        currentProgress= requests.get(f"{DB_URL}/cookies/{cookieId}").json()
        if currentProgress<10:
            qnsId=questionMapping[currentProgress]
            return requests.get(f"{DB_URL}/qnsInfo/{qnsId}").json()
        else:
            return "All questions answered"
    
@blp.route("/ansQns")
class AnsQns(MethodView):
    def post(self):
        response=request.json["response"]
        cookieId=request.cookies.get("GreenFlags")
        currentProgress= requests.get(f"{DB_URL}/cookies/{cookieId}").json()
        qnsId=questionMapping[currentProgress]
        userId=requests.get(f"{DB_URL}/cookiesUser/{cookieId}").json()
        #check qns type and embed if needed or attach questionerId
        body={
            "response":response,
            "userId":userId,
            "qnsId":qnsId,
            
        }
        qnsType= requests.get(f"{DB_URL}/qnsInfo/{qnsId}").json()["type"]
        print("QnsType",qnsType)
        if qnsType==2:
            print("Embedding response")
            body["encoding"]=json.dumps(fastEmbedding(response))
        elif qnsType==3: #response provided is user's question
            requests.post(f"{DB_URL}/customQns",json={"question":response,"questionerId":userId,"type":3}).json()
            requests.post(f"{DB_URL}/cookiesUser/{cookieId}",json={})
            return "2"
        response= requests.post(f"{DB_URL}/response", json=body).json()
        if response:
            cookieProgressUrl=f"{DB_URL}/cookiesProgress/{cookieId}"
            status= requests.put(cookieProgressUrl).json()
            return str(status) #0 for incomplete, 1 for complete qns but still have own qns, 2 for complete
        else:
            return "Failed to update progress",400
        
@blp.route("/checkStatus")
class CheckStatus(MethodView):
    def get(self):
        cookieId=request.cookies.get("GreenFlags")
        cookie= requests.get(f"{DB_URL}/cookies/{cookieId}").json()
        if cookie["isCompleted"]:
            return jsonify(2)
        elif cookie["currentProgress"]>=10:
            return jsonify(1)
        else:
            return jsonify(0)