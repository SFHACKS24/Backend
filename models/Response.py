from db import db
from sqlalchemy import JSON

class ResponseModel(db.Model):
    __tablename__ = 'responses'
    id= db.Column(db.String, primary_key=True)
    response= db.Column(db.String, nullable=False)

    userId= db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    userInfo=db.relationship('UserModel', back_populates="userResponses")

    qnsId= db.Column(db.String, db.ForeignKey('qnsInfo.id'), nullable=False)
    qnsInfo=db.relationship('QnsInfoModel', back_populates="qnsResponses")

    encoding= db.Column(JSON) #for structured responses