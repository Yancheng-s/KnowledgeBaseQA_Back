from datetime import datetime

from database.database import db

class KBSconstruction_pojo(db.Model):
    __tablename__ = 'knowledge'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    kon_name = db.Column(db.String(255), nullable=False)
    kon_describe = db.Column(db.String(255), nullable=False)
    emb_moddle = db.Column(db.String(255), nullable=False)
    chunk = db.Column(db.String(255), nullable=False)
    sentence_identifier = db.Column(db.String(255), nullable=False)
    estimated_length_per_senction = db.Column(db.Integer, nullable=False)
    segmental_overlap_length = db.Column(db.Integer, nullable=False)
    excel_header_processing = db.Column(db.String(10), nullable=False)
    similarity = db.Column(db.String(255), nullable=False)
    MROD = db.Column(db.String(255), nullable=False)
    sorting_config = db.Column(db.String(255), nullable=False)
    file_list = db.Column(db.Text, nullable=False)
    update_time = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        result = {}
        for c in self.__table__.columns:
            value = getattr(self, c.name)
            # 如果是 datetime 类型，格式化为字符串
            if isinstance(value, datetime):
                result[c.name] = value.strftime('%Y-%m-%d %H:%M:%S') if value else None
            else:
                result[c.name] = value
        return result