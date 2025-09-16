# src/utils/conversation_manager.py

from database.database import db
from src.pojo.conversation_history_pojo import ConversationHistory

# 全局缓存字典，用于存储对话历史
conversation_cache = {}

class ConversationManager:
    @staticmethod
    def load_conversation_history(user_id, agent_id, llm_memory, max_rounds=10):
        """
        加载对话历史
        :param user_id: 用户 ID
        :param agent_id: 智能体 ID
        :param llm_memory: 是否开启持久化存储 ("y" 或 "n")
        :param max_rounds: 最大加载的对话轮数
        :return: 对话历史列表
        """
        # 生成唯一键
        key = f"{user_id}_{agent_id}"

        # 优先从缓存加载
        if key in conversation_cache:
            return conversation_cache[key][-max_rounds:]  # 取最近几轮对话

        # 如果缓存为空且 llm_memory 为 "y"，从数据库加载并同步到缓存
        if llm_memory == "y":
            history = ConversationHistory.query.filter_by(
                user_id=user_id, agent_id=agent_id
            ).order_by(ConversationHistory.timestamp.desc()).limit(max_rounds).all()
            history_data = [(h.message, h.response) for h in reversed(history)]

            # 同步到缓存
            conversation_cache[key] = history_data
            return history_data

        # 如果缓存为空且 llm_memory 为 "n"，返回空列表
        return []

    @staticmethod
    def save_conversation(user_id, agent_id, message, response, llm_memory):
        """
        保存对话历史
        :param user_id: 用户 ID
        :param agent_id: 智能体 ID
        :param message: 用户消息
        :param response: 智能体响应
        :param llm_memory: 是否开启持久化存储 ("y" 或 "n")
        """
        # 生成唯一键
        key = f"{user_id}_{agent_id}"

        if llm_memory == "y":
            # 存储到数据库
            new_record = ConversationHistory(
                user_id=user_id,
                agent_id=agent_id,
                message=message,
                response=response
            )
            db.session.add(new_record)
            db.session.commit()

        # 同步存储到缓存
        if key not in conversation_cache:
            conversation_cache[key] = []
        conversation_cache[key].append((message, response))
