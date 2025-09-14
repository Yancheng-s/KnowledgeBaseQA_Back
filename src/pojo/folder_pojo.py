from flask_sqlalchemy import SQLAlchemy

from database.database import db

class Folder(db.Model):
    __tablename__ = 'folder'  # 数据库中的表名
    id = db.Column(db.Integer, primary_key=True)
    folder_name = db.Column(db.String(100))