from db import db

class QnsInfoModel(db.Model):
    __tablename__ = 'qnsInfo'
    id= db.Column(db.String, primary_key=True)
    question= db.Column(db.String, nullable=False)
    type= db.Column(db.Integer, nullable=False)
    questionerId= db.Column(db.String, db.ForeignKey('users.id'), nullable=True)

    qnsResponses=db.relationship('ResponseModel', back_populates="qnsInfo")

    questioner=db.relationship('UserModel', back_populates="posedQns", uselist=False)
