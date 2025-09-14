# tongti_Trub.py

import os
from openai import OpenAI

def get_chat_completion(model_name="qwen-plus", messages=None):
    """
    调用阿里云的OpenAI兼容接口，生成对话补全。

    参数:
        model_name (str): 使用的模型名称，默认为 `qwen-plus`。
        messages (list): 对话消息列表，格式为 [{"role": "system/user", "content": "消息内容"}]。

    返回:
        dict: 包含模型返回结果的字典。
    """
    # 初始化客户端
    client = OpenAI(
        api_key="sk-c9b8659683a541bfaa8580448ca67766",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    # 调用API并返回结果
    completion = client.chat.completions.create(
        model=model_name,
        messages=messages,
    )
    return completion.model_dump()
