# API 使用示例 / API Usage Examples

## 中文示例

### 1. 创建智能体
```bash
curl -X POST http://localhost:5000/addAgent \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "客服助手",
    "agent_state": "active",
    "agent_id": 123456,
    "llm_api": "通义千问",
    "llm_prompt": "你是一个专业的客服助手，请友好地回答用户问题。",
    "llm_image": "y",
    "llm_knowledge": "产品知识库,常见问题库",
    "llm_file": "y",
    "llm_internet": "y",
    "llm_memory": "y",
    "llm_maximum_length_of_reply": 2048,
    "llm_carry_number_of_rounds_of_context": 10,
    "llm_temperature_coefficient": "0.8"
  }'
```

### 2. 上传文件
```bash
curl -X POST http://localhost:5000/fileupload \
  -F "file=@document.pdf" \
  -F "file_class=产品文档"
```

### 3. 智能体对话
```bash
curl -X POST http://localhost:5000/processAgent/123456 \
  -H "Content-Type: application/json" \
  -d '{
    "message": "请介绍一下你们的产品",
    "user_id": "user123",
    "llm_knowledge": "产品知识库",
    "llm_image": "n",
    "llm_file": "n",
    "llm_internet": "y"
  }'
```

### 4. 创建知识库
```bash
curl -X POST http://localhost:5000/addKBS \
  -H "Content-Type: application/json" \
  -d '{
    "kon_name": "产品知识库",
    "kon_describe": "包含所有产品相关信息的知识库",
    "emb_moddle": "text-embedding-ada-002",
    "chunk": "1000",
    "sentence_identifier": "。",
    "estimated_length_per_senction": 100,
    "segmental_overlap_length": 200,
    "excel_header_processing": "y",
    "similarity": "0.8",
    "MROD": "MMR",
    "sorting_config": "relevance",
    "file_list": "document1.pdf,document2.docx"
  }'
```

## English Examples

### 1. Create Agent
```bash
curl -X POST http://localhost:5000/addAgent \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "Customer Service Assistant",
    "agent_state": "active",
    "agent_id": 123456,
    "llm_api": "Tongyi Qianwen",
    "llm_prompt": "You are a professional customer service assistant. Please answer user questions in a friendly manner.",
    "llm_image": "y",
    "llm_knowledge": "product_knowledge,faq_knowledge",
    "llm_file": "y",
    "llm_internet": "y",
    "llm_memory": "y",
    "llm_maximum_length_of_reply": 2048,
    "llm_carry_number_of_rounds_of_context": 10,
    "llm_temperature_coefficient": "0.8"
  }'
```

### 2. Upload File
```bash
curl -X POST http://localhost:5000/fileupload \
  -F "file=@document.pdf" \
  -F "file_class=product_documents"
```

### 3. Agent Conversation
```bash
curl -X POST http://localhost:5000/processAgent/123456 \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Please introduce your products",
    "user_id": "user123",
    "llm_knowledge": "product_knowledge",
    "llm_image": "n",
    "llm_file": "n",
    "llm_internet": "y"
  }'
```

### 4. Create Knowledge Base
```bash
curl -X POST http://localhost:5000/addKBS \
  -H "Content-Type: application/json" \
  -d '{
    "kon_name": "product_knowledge",
    "kon_describe": "Knowledge base containing all product-related information",
    "emb_moddle": "text-embedding-ada-002",
    "chunk": "1000",
    "sentence_identifier": ".",
    "estimated_length_per_senction": 100,
    "segmental_overlap_length": 200,
    "excel_header_processing": "y",
    "similarity": "0.8",
    "MROD": "MMR",
    "sorting_config": "relevance",
    "file_list": "document1.pdf,document2.docx"
  }'
```

## Python SDK 示例

### 安装SDK
```bash
pip install requests
```

### Python 客户端代码
```python
import requests
import json

class LangFlowClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    def create_agent(self, agent_data):
        response = requests.post(
            f"{self.base_url}/addAgent",
            json=agent_data
        )
        return response.json()
    
    def upload_file(self, file_path, file_class=None):
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'file_class': file_class} if file_class else {}
            response = requests.post(
                f"{self.base_url}/fileupload",
                files=files,
                data=data
            )
        return response.json()
    
    def chat_with_agent(self, agent_id, message, user_id, **kwargs):
        data = {
            "message": message,
            "user_id": user_id,
            **kwargs
        }
        response = requests.post(
            f"{self.base_url}/processAgent/{agent_id}",
            json=data
        )
        return response.json()

# 使用示例
client = LangFlowClient()

# 创建智能体
agent_data = {
    "agent_name": "AI助手",
    "agent_state": "active",
    "agent_id": 123456,
    "llm_api": "通义千问",
    "llm_prompt": "你是一个有用的AI助手",
    "llm_image": "y",
    "llm_knowledge": "知识库1",
    "llm_file": "y",
    "llm_internet": "y",
    "llm_memory": "y",
    "llm_maximum_length_of_reply": 2048,
    "llm_carry_number_of_rounds_of_context": 10,
    "llm_temperature_coefficient": "0.8"
}

result = client.create_agent(agent_data)
print("智能体创建结果:", result)

# 与智能体对话
chat_result = client.chat_with_agent(
    agent_id=123456,
    message="你好，请介绍一下自己",
    user_id="user123",
    llm_knowledge="知识库1"
)
print("对话结果:", chat_result)
```
