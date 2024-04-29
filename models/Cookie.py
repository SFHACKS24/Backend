from sqlalchemy import Boolean
from db import db

class CookieModel(db.Model):
    __tablename__ = 'cookies'
    id= db.Column(db.String, primary_key=True)
    userId= db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    currentProgress= db.Column(db.Integer, nullable=False)
    isCompleted= db.Column(Boolean, nullable=False)
    hasDirectRecommendation= db.Column(Boolean, nullable=False)