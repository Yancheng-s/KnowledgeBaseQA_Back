from database.database import db

class ConversationHistory(db.Model):

    __tablename__ = 'conversationHistory'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), nullable=False)  # 用户标识
    agent_id = db.Column(db.String(255), nullable=False)  # 智能体标识
    message = db.Column(db.Text, nullable=False)  # 用户消息
    response = db.Column(db.Text, nullable=False)  # 智能体响应
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
