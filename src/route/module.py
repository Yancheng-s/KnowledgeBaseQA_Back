# module.py
from src.file.folder import folder
from src.file.KBSconstruction import KBSconstruction
from src.file.agent import agent
from src.file.model import model

def register_routes(app):
    folder(app)
    KBSconstruction(app)
    agent(app)
    model(app)

