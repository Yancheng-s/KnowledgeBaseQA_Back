from database.database import db

class File(db.Model):
    __tablename__ = 'file'
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255))
    file_path = db.Column(db.String(255))
    file_class = db.Column(db.String(255))
    file_size = db.Column(db.Integer())
    file_time = db.Column(db.DateTime, default=db.func.current_timestamp())