# model_pojo.py
from database.database import db

class ModelPojo(db.Model):
    __tablename__ = 'model'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    model_name = db.Column(db.String(255), nullable=False)
    model_presentation = db.Column(db.String(255))
    model_key = db.Column(db.String(255), nullable=False)
    model_date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<ModelPojo(id={self.id}, model_name='{self.model_name}', model_presentation='{self.model_presentation}', model_key='{self.model_key}', model_date='{self.model_date}')>"
