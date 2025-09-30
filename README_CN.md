# LangFlow Chat Backend - 智能对话后端系统

## 项目简介

LangFlow Chat Backend 是一个基于 Flask 的智能对话后端系统，专为构建数字人类应用而设计。该系统集成了文档处理、向量存储、模型调用、文件管理、知识库构建等核心功能，为AI智能体提供强大的后端支持。

数字人及智能体前后端项目分别放在两个代码仓库：

1.前端代码仓库： https://gitee.com/garveyer/lang-flow_3-d-digital-human_-front

2.后端代码仓库： https://gitee.com/garveyer/lang-flow_3-d-digital-human_-back


## 🚀 核心功能

### 1. 智能体管理 (Agent Management)
- **智能体创建与配置**：支持创建和配置AI智能体，包括模型选择、提示词设置、功能开关等
- **多模型支持**：集成多种大语言模型，支持OpenAI、阿里云通义千问等
- **智能体状态管理**：支持智能体的启用/禁用状态控制
- **参数调优**：支持温度系数、最大回复长度、上下文轮数等参数配置

### 2. 文件管理系统 (File Management)
- **多格式文件上传**：支持PDF、Word、Excel、PPT、图片、视频、音频等多种格式
- **OSS云存储集成**：集成阿里云OSS对象存储服务，支持大文件上传
- **文件预览功能**：支持在线预览Office文档、PDF、图片、视频等
- **文件分类管理**：支持文件夹分类和文件搜索功能
- **文件大小统计**：自动计算和记录文件大小信息

### 3. 知识库构建 (Knowledge Base Construction)
- **文档向量化**：支持文档分块、向量化存储
- **多知识库管理**：支持创建和管理多个独立的知识库
- **FAISS索引存储**：使用FAISS向量数据库进行高效检索
- **相似度搜索**：支持基于语义的文档检索
- **知识库更新**：支持知识库的增量更新和重建

### 4. 智能对话处理 (Intelligent Chat Processing)
- **多模态输入**：支持文本、图片、文件等多种输入方式
- **上下文记忆**：支持对话历史管理和上下文保持
- **工具函数集成**：集成图片理解、文件解析、网络搜索等工具
- **并行处理**：支持知识库搜索和工具调用的并行处理
- **实时响应**：优化的响应速度和用户体验

### 5. 模型管理 (Model Management)
- **模型配置**：支持多种大语言模型的配置和管理
- **API密钥管理**：安全的API密钥存储和管理
- **模型切换**：支持动态切换不同的语言模型
- **性能监控**：支持Token使用统计和性能监控

## 🏗️ 技术架构

### 后端框架
- **Flask**：轻量级Web框架
- **SQLAlchemy**：ORM数据库操作
- **MySQL**：关系型数据库存储
- **FAISS**：向量数据库检索

### 核心依赖
- **LangChain**：大语言模型应用框架
- **OpenAI**：大语言模型API
- **PIL/Pillow**：图像处理
- **PyPDF2**：PDF文档处理
- **python-docx**：Word文档处理
- **pandas**：数据处理
- **requests**：HTTP请求处理

### 云服务集成
- **阿里云OSS**：对象存储服务
- **阿里云通义千问**：大语言模型服务
- **Tavily**：网络搜索服务

## 📁 项目结构

```
langflow-chat-back/
├── main.py                          # 应用入口文件
├── database/                        # 数据库配置
│   └── database.py                  # 数据库连接配置
├── src/                            # 核心源代码
│   ├── file/                       # 文件处理模块
│   │   ├── agent.py                # 智能体管理
│   │   ├── folder.py               # 文件夹和文件管理
│   │   ├── KBSconstruction.py     # 知识库构建
│   │   └── model.py                # 模型管理
│   ├── pojo/                       # 数据模型定义
│   │   ├── agent_pojo.py          # 智能体数据模型
│   │   ├── file_pojo.py           # 文件数据模型
│   │   ├── folder_pojo.py          # 文件夹数据模型
│   │   ├── KBSconstruction_pojo.py # 知识库数据模型
│   │   ├── model_pojo.py          # 模型数据模型
│   │   └── conversation_history_pojo.py # 对话历史模型
│   ├── route/                      # 路由管理
│   │   └── module.py              # 路由注册
│   └── utils/                      # 工具类模块
│       ├── chunk_documents.py     # 文档分块处理
│       ├── load_document.py       # 文档加载
│       ├── vectorize_documents.py # 文档向量化
│       ├── OSSFileUpload.py       # OSS文件上传
│       ├── download_cleanup_file.py # 文件下载清理
│       ├── tongti_Trub.py         # 通义千问集成
│       └── temporary_message/     # 临时消息处理
│           ├── conversation_manager.py # 对话管理
│           ├── model_loader.py    # 模型加载器
│           ├── model_service.py   # 模型服务
│           ├── prompt_builder.py  # 提示词构建
│           ├── search_multiple_kbs.py # 多知识库搜索
│           └── tool_functions.py  # 工具函数
├── test/                          # 测试文件
│   └── test_internet_search.py   # 网络搜索测试
├── README.md                      # 中文说明文档
├── README.en.md                   # 英文说明文档
└── requirements.txt               # 依赖包列表
```

## 🛠️ 安装与配置

### 环境要求
- Python 3.8+
- MySQL 5.7+
- 8GB+ RAM (推荐)

### 1. 克隆项目
```bash
git clone <repository-url>
cd langflow-chat-back
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 数据库配置
1. 创建MySQL数据库：
```sql
CREATE DATABASE chainflow CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 修改数据库连接配置（`main.py`）：
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://用户名:密码@主机地址:端口/数据库名'
```

### 4. 环境变量配置
创建 `.env` 文件并配置以下变量：
```env
# 阿里云配置
DASHSCOPE_API_KEY=your_dashscope_api_key
OSS_ACCESS_KEY_ID=your_oss_access_key_id
OSS_ACCESS_KEY_SECRET=your_oss_access_key_secret
OSS_BUCKET_NAME=your_bucket_name
OSS_REGION=cn-beijing

# 其他API配置
TAVILY_API_KEY=your_tavily_api_key
```

### 5. 启动服务
```bash
python main.py
```

服务将在 `http://localhost:5000` 启动

## 📚 API 接口文档

### 智能体管理接口

#### 创建智能体
```http
POST /addAgent
Content-Type: application/json

{
    "agent_name": "智能体名称",
    "agent_state": "active",
    "agent_id": 123456,
    "llm_api": "通义千问",
    "llm_prompt": "你是一个专业的助手...",
    "llm_image": "y",
    "llm_knowledge": "知识库1,知识库2",
    "llm_file": "y",
    "llm_internet": "y",
    "llm_memory": "y",
    "llm_maximum_length_of_reply": 2048,
    "llm_carry_number_of_rounds_of_context": 10,
    "llm_temperature_coefficient": "0.8"
}
```

#### 处理智能体对话
```http
POST /processAgent/{agent_id}
Content-Type: application/json

{
    "message": "用户消息",
    "user_id": "user123",
    "llm_knowledge": "知识库1,知识库2",
    "llm_image": "y",
    "llm_file": "y",
    "llm_internet": "y"
}
```

### 文件管理接口

#### 文件上传
```http
POST /fileupload
Content-Type: multipart/form-data

file: [文件]
file_class: "分类名称"
```

#### 文件列表查询
```http
POST /selectfilelist
Content-Type: application/json

{
    "folder_name": "分类名称"
}
```

#### 文件预览
```http
POST /getfilepreview
Content-Type: application/json

{
    "file_name": "文件名",
    "file_path": "文件URL"
}
```

### 知识库管理接口

#### 创建知识库
```http
POST /addKBS
Content-Type: application/json

{
    "kon_name": "知识库名称",
    "kon_describe": "知识库描述",
    "emb_moddle": "embedding模型",
    "chunk": "分块大小",
    "sentence_identifier": "句子标识符",
    "estimated_length_per_senction": 100,
    "segmental_overlap_length": 20,
    "excel_header_processing": "y",
    "similarity": "0.8",
    "MROD": "检索模式",
    "sorting_config": "排序配置",
    "file_list": "文件列表"
}
```

#### 知识库搜索
```http
POST /searchKBS
Content-Type: application/json

{
    "kon_name": "知识库名称",
    "query": "搜索查询",
    "top_k": 5
}
```

### 模型管理接口

#### 添加模型
```http
POST /addModel
Content-Type: application/json

{
    "model_name": "模型名称",
    "model_presentation": "模型描述",
    "model_key": "API密钥"
}
```

#### 模型列表
```http
GET /listModels
```

## 🔧 配置说明

### 数据库配置
系统使用MySQL数据库存储以下信息：
- 智能体配置信息
- 文件元数据
- 知识库配置
- 对话历史记录
- 模型配置信息

### 文件存储配置
- 使用阿里云OSS作为文件存储服务
- 支持大文件上传和下载
- 自动生成文件访问URL

### 向量存储配置
- 使用FAISS作为向量数据库
- 支持多种embedding模型
- 支持增量更新和重建

## 🚀 部署指南

### Docker部署
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "main.py"]
```

### 生产环境配置
1. 使用Gunicorn作为WSGI服务器
2. 配置Nginx反向代理
3. 设置SSL证书
4. 配置日志轮转
5. 设置监控和告警

## 🧪 测试

### 运行测试
```bash
python -m pytest test/
```

### 测试覆盖
- 单元测试：核心功能模块
- 集成测试：API接口测试
- 性能测试：并发处理能力

## 📊 性能优化

### 缓存策略
- 模型实例缓存
- 知识库索引缓存
- 对话历史缓存

### 并发处理
- 多线程处理知识库搜索
- 异步文件上传
- 并行工具调用

### 数据库优化
- 索引优化
- 查询优化
- 连接池配置

## 🔒 安全考虑

### API安全
- 输入验证和过滤
- SQL注入防护
- XSS攻击防护

### 数据安全
- 敏感信息加密存储
- API密钥安全管理
- 文件访问权限控制

## 🤝 贡献指南

### 开发流程
1. Fork项目
2. 创建功能分支
3. 提交代码更改
4. 创建Pull Request

### 代码规范
- 遵循PEP 8编码规范
- 添加必要的注释和文档
- 编写单元测试

## 📄 许可证

本项目采用MIT许可证。详情请查看 [LICENSE](LICENSE) 文件。

## 📞 支持与联系

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件
- 参与讨论

## 🔄 更新日志

### v1.0.0
- 初始版本发布
- 基础功能实现
- 文档完善

---

**注意**：本项目正在积极开发中，功能可能会有所变化。请关注最新更新。
