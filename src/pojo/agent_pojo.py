from database.database import db

class AgentPojo(db.Model):
    __tablename__ = 'agent'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    agent_name = db.Column(db.String(255), nullable=False, comment='智能体名称')
    agent_state = db.Column(db.String(255), nullable=False)
    agent_id = db.Column(db.BigInteger, nullable=False)
    llm_api = db.Column(db.String(255))
    llm_prompt = db.Column(db.String(255))
    llm_image = db.Column(db.String(255))
    llm_knowledge = db.Column(db.String(255))
    llm_file = db.Column(db.String(255), comment='这里上传的文件只暂存LLM提示词中')
    llm_internet = db.Column(db.String(255))
    llm_memory = db.Column(db.Text)
    llm_maximum_length_of_reply = db.Column(db.Double)
    llm_carry_number_of_rounds_of_context = db.Column(db.Integer)
    llm_temperature_coefficient = db.Column(db.String(255))