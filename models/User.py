from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float
from db import db


class UserModel(db.Model):
    __tablename__ = 'users'
    id= db.Column(db.String, primary_key=True)
    name= db.Column(db.String, nullable=False)
    isMale= db.Column(db.Boolean, nullable=False)
    age= db.Column(db.Integer, nullable=False)
    occupation= db.Column(db.String, nullable=False)
    location= db.Column(db.String, nullable=False)
    budget= db.Column(db.Integer, nullable=False)
    hasRoom= db.Column(db.Boolean, nullable=False)

    
    posedQns=db.relationship('QnsInfoModel', back_populates="questioner", uselist=False)
    userResponses= db.relationship('ResponseModel', back_populates="userInfo")
    #posed Qns
