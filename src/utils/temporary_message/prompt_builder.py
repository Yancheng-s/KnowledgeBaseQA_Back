# src/utils/prompt_builder.py
class PromptBuilder:
    @staticmethod
    def build_prompt(llm_prompt, llm_image, llm_file, llm_internet, message):
        prompt = llm_prompt + "\n"

        if llm_image == "y":
            prompt += "[图片理解功能已开启]\n"
        if llm_file == "y":
            prompt += "[文件解析功能已开启]\n"
        if llm_internet == "y":
            prompt += "[联网搜索功能已开启]\n"

        prompt += f"用户输入: {message}"
        return prompt
