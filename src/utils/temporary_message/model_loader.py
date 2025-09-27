# src/utils/model_loader.py
from langchain_community.chat_models import ChatOpenAI
from langchain_community.chat_models import ChatTongyi

def load_model(model_name: str, api_key: str, temperature: float = 0.8, max_tokens: int = 2048):
    # 判断模型类型
    if model_name.startswith("qwen"):
        # 阿里云 Qwen
        return ChatTongyi(
            model=model_name,
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/api/v1",
            temperature=temperature,
            max_tokens=max_tokens
        )
    elif model_name.startswith("deepseek"):
        # Deepseek
        return ChatOpenAI(
            model_name=model_name,
            openai_api_key=api_key,
            base_url="https://api.deepseek.com/v1",
            temperature=temperature,
            max_tokens=max_tokens
        )
    else:
        raise ValueError(f"不支持的模型: {model_name}")
