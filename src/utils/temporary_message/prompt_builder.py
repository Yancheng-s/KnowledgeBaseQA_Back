# src/utils/prompt_builder.py
class PromptBuilder:
    @staticmethod
    def build_prompt_with_history(llm_prompt, llm_image, llm_file, llm_internet, message, history):
        prompt = llm_prompt + "\n"

        if llm_image == "y":
            prompt += "[图片理解功能已开启]\n"
        if llm_file == "y":
            prompt += "[文件解析功能已开启]\n"
        if llm_internet == "y":
            prompt += "[联网搜索功能已开启]\n"

        # 添加历史对话
        if history:
            prompt += "\n对话历史:\n"
            for msg, resp in history:
                prompt += f"用户: {msg}\n智能体: {resp}\n"

        prompt += f"\n当前输入: {message}"
        return prompt
