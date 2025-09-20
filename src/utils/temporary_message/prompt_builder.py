# src/utils/prompt_builder.py
from datetime import datetime

class PromptBuilder:
    @staticmethod
    def build_prompt_with_history(llm_prompt, llm_image, llm_file, llm_internet, message, history, max_history_rounds=5):
        """
        构建包含历史对话和功能开关信息的提示词
        :param llm_prompt: 初始 Prompt
        :param llm_image: 图片理解功能开关（"y" 或其他值）
        :param llm_file: 文件解析功能开关（"y" 或其他值）
        :param llm_internet: 联网搜索功能开关（"y" 或其他值）
        :param message: 当前用户输入
        :param history: 历史对话记录（列表形式，每个元素为 (msg, resp) 元组）
        :param max_history_rounds: 最大保留的历史对话轮数
        :return: 构建好的提示词字符串
        """
        # 初始化提示词
        prompt = llm_prompt + "\n"

        # 定义功能开关描述
        features = {
            "llm_image": "图片理解功能已开启",
            "llm_file": "文件解析功能已开启",
            "llm_internet": "联网搜索功能已开启"
        }

        # 添加功能开关信息
        for feature_flag, feature_desc in features.items():
            if locals()[feature_flag] == "y":
                prompt += f"[{feature_desc}]\n"

        # 添加时间戳
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prompt += f"\n当前时间: {timestamp}"

        # 添加历史对话（限制最大轮数）
        if history:
            prompt += "\n对话历史:\n"
            history = history[-max_history_rounds:]  # 截取最近几轮对话
            for msg, resp in history:
                prompt += f"用户: {msg}\n智能体: {resp}\n"

        # 添加当前输入
        prompt += f"\n当前输入: {message}"
        return prompt

