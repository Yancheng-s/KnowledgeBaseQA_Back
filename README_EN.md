# LangFlow Chat Backend - Intelligent Conversation Backend System

## Project Overview

LangFlow Chat Backend is a Flask-based intelligent conversation backend system designed for building digital human applications. The system integrates core functionalities including document processing, vector storage, model invocation, file management, and knowledge base construction, providing powerful backend support for AI agents.

## 🚀 Core Features

### 1. Agent Management
- **Agent Creation & Configuration**: Support for creating and configuring AI agents, including model selection, prompt settings, and feature toggles
- **Multi-Model Support**: Integration with various large language models, supporting OpenAI, Alibaba Cloud Tongyi Qianwen, and more
- **Agent State Management**: Support for enabling/disabling agent states
- **Parameter Tuning**: Configuration support for temperature coefficients, maximum reply length, context rounds, and other parameters

### 2. File Management System
- **Multi-Format File Upload**: Support for PDF, Word, Excel, PPT, images, videos, audio, and other formats
- **OSS Cloud Storage Integration**: Integration with Alibaba Cloud OSS object storage service, supporting large file uploads
- **File Preview Functionality**: Support for online preview of Office documents, PDFs, images, videos, etc.
- **File Classification Management**: Support for folder classification and file search functionality
- **File Size Statistics**: Automatic calculation and recording of file size information

### 3. Knowledge Base Construction
- **Document Vectorization**: Support for document chunking and vectorized storage
- **Multi-Knowledge Base Management**: Support for creating and managing multiple independent knowledge bases
- **FAISS Index Storage**: Using FAISS vector database for efficient retrieval
- **Similarity Search**: Support for semantic-based document retrieval
- **Knowledge Base Updates**: Support for incremental updates and reconstruction of knowledge bases

### 4. Intelligent Chat Processing
- **Multi-Modal Input**: Support for text, images, files, and other input methods
- **Context Memory**: Support for conversation history management and context retention
- **Tool Function Integration**: Integration of image understanding, file parsing, web search, and other tools
- **Parallel Processing**: Support for parallel processing of knowledge base search and tool calls
- **Real-Time Response**: Optimized response speed and user experience

### 5. Model Management
- **Model Configuration**: Support for configuration and management of various large language models
- **API Key Management**: Secure storage and management of API keys
- **Model Switching**: Support for dynamic switching between different language models
- **Performance Monitoring**: Support for Token usage statistics and performance monitoring

## 🏗️ Technical Architecture

### Backend Framework
- **Flask**: Lightweight web framework
- **SQLAlchemy**: ORM database operations
- **MySQL**: Relational database storage
- **FAISS**: Vector database retrieval

### Core Dependencies
- **LangChain**: Large language model application framework
- **OpenAI**: Large language model API
- **PIL/Pillow**: Image processing
- **PyPDF2**: PDF document processing
- **python-docx**: Word document processing
- **pandas**: Data processing
- **requests**: HTTP request handling

### Cloud Service Integration
- **Alibaba Cloud OSS**: Object storage service
- **Alibaba Cloud Tongyi Qianwen**: Large language model service
- **Tavily**: Web search service

## 📁 Project Structure

```
langflow-chat-back/
├── main.py                          # Application entry point
├── database/                        # Database configuration
│   └── database.py                  # Database connection configuration
├── src/                            # Core source code
│   ├── file/                       # File processing modules
│   │   ├── agent.py                # Agent management
│   │   ├── folder.py               # Folder and file management
│   │   ├── KBSconstruction.py      # Knowledge base construction
│   │   └── model.py                # Model management
│   ├── pojo/                       # Data model definitions
│   │   ├── agent_pojo.py          # Agent data model
│   │   ├── file_pojo.py           # File data model
│   │   ├── folder_pojo.py          # Folder data model
│   │   ├── KBSconstruction_pojo.py # Knowledge base data model
│   │   ├── model_pojo.py          # Model data model
│   │   └── conversation_history_pojo.py # Conversation history model
│   ├── route/                      # Route management
│   │   └── module.py              # Route registration
│   └── utils/                      # Utility modules
│       ├── chunk_documents.py     # Document chunking processing
│       ├── load_document.py       # Document loading
│       ├── vectorize_documents.py # Document vectorization
│       ├── OSSFileUpload.py       # OSS file upload
│       ├── download_cleanup_file.py # File download cleanup
│       ├── tongti_Trub.py         # Tongyi Qianwen integration
│       └── temporary_message/     # Temporary message processing
│           ├── conversation_manager.py # Conversation management
│           ├── model_loader.py    # Model loader
│           ├── model_service.py   # Model service
│           ├── prompt_builder.py  # Prompt builder
│           ├── search_multiple_kbs.py # Multi-knowledge base search
│           └── tool_functions.py  # Tool functions
├── test/                          # Test files
│   └── test_internet_search.py  # Internet search test
├── README.md                      # Chinese documentation
├── README.en.md                   # English documentation
└── requirements.txt               # Dependency list
```

## 🛠️ Installation & Configuration

### Environment Requirements
- Python 3.8+
- MySQL 5.7+
- 8GB+ RAM (recommended)

### 1. Clone the Project
```bash
git clone <repository-url>
cd langflow-chat-back
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Configuration
1. Create MySQL database:
```sql
CREATE DATABASE chainflow CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Modify database connection configuration (`main.py`):
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@host:port/database_name'
```

### 4. Environment Variables Configuration
Create `.env` file and configure the following variables:
```env
# Alibaba Cloud Configuration
DASHSCOPE_API_KEY=your_dashscope_api_key
OSS_ACCESS_KEY_ID=your_oss_access_key_id
OSS_ACCESS_KEY_SECRET=your_oss_access_key_secret
OSS_BUCKET_NAME=your_bucket_name
OSS_REGION=cn-beijing

# Other API Configuration
TAVILY_API_KEY=your_tavily_api_key
```

### 5. Start the Service
```bash
python main.py
```

The service will start at `http://localhost:5000`

## 📚 API Documentation

### Agent Management APIs

#### Create Agent
```http
POST /addAgent
Content-Type: application/json

{
    "agent_name": "Agent Name",
    "agent_state": "active",
    "agent_id": 123456,
    "llm_api": "Tongyi Qianwen",
    "llm_prompt": "You are a professional assistant...",
    "llm_image": "y",
    "llm_knowledge": "knowledge_base1,knowledge_base2",
    "llm_file": "y",
    "llm_internet": "y",
    "llm_memory": "y",
    "llm_maximum_length_of_reply": 2048,
    "llm_carry_number_of_rounds_of_context": 10,
    "llm_temperature_coefficient": "0.8"
}
```

#### Process Agent Conversation
```http
POST /processAgent/{agent_id}
Content-Type: application/json

{
    "message": "User message",
    "user_id": "user123",
    "llm_knowledge": "knowledge_base1,knowledge_base2",
    "llm_image": "y",
    "llm_file": "y",
    "llm_internet": "y"
}
```

### File Management APIs

#### File Upload
```http
POST /fileupload
Content-Type: multipart/form-data

file: [file]
file_class: "category_name"
```

#### File List Query
```http
POST /selectfilelist
Content-Type: application/json

{
    "folder_name": "category_name"
}
```

#### File Preview
```http
POST /getfilepreview
Content-Type: application/json

{
    "file_name": "filename",
    "file_path": "file_url"
}
```

### Knowledge Base Management APIs

#### Create Knowledge Base
```http
POST /addKBS
Content-Type: application/json

{
    "kon_name": "Knowledge Base Name",
    "kon_describe": "Knowledge Base Description",
    "emb_moddle": "embedding_model",
    "chunk": "chunk_size",
    "sentence_identifier": "sentence_identifier",
    "estimated_length_per_senction": 100,
    "segmental_overlap_length": 20,
    "excel_header_processing": "y",
    "similarity": "0.8",
    "MROD": "retrieval_mode",
    "sorting_config": "sorting_configuration",
    "file_list": "file_list"
}
```

#### Knowledge Base Search
```http
POST /searchKBS
Content-Type: application/json

{
    "kon_name": "Knowledge Base Name",
    "query": "search query",
    "top_k": 5
}
```

### Model Management APIs

#### Add Model
```http
POST /addModel
Content-Type: application/json

{
    "model_name": "Model Name",
    "model_presentation": "Model Description",
    "model_key": "API Key"
}
```

#### Model List
```http
GET /listModels
```

## 🔧 Configuration Guide

### Database Configuration
The system uses MySQL database to store the following information:
- Agent configuration information
- File metadata
- Knowledge base configuration
- Conversation history records
- Model configuration information

### File Storage Configuration
- Uses Alibaba Cloud OSS as file storage service
- Supports large file upload and download
- Automatically generates file access URLs

### Vector Storage Configuration
- Uses FAISS as vector database
- Supports multiple embedding models
- Supports incremental updates and reconstruction

## 🚀 Deployment Guide

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "main.py"]
```

### Production Environment Configuration
1. Use Gunicorn as WSGI server
2. Configure Nginx reverse proxy
3. Set up SSL certificates
4. Configure log rotation
5. Set up monitoring and alerts

## 🧪 Testing

### Run Tests
```bash
python -m pytest test/
```

### Test Coverage
- Unit tests: Core functionality modules
- Integration tests: API interface tests
- Performance tests: Concurrent processing capabilities

## 📊 Performance Optimization

### Caching Strategy
- Model instance caching
- Knowledge base index caching
- Conversation history caching

### Concurrent Processing
- Multi-threaded knowledge base search processing
- Asynchronous file upload
- Parallel tool calls

### Database Optimization
- Index optimization
- Query optimization
- Connection pool configuration

## 🔒 Security Considerations

### API Security
- Input validation and filtering
- SQL injection protection
- XSS attack protection

### Data Security
- Encrypted storage of sensitive information
- Secure API key management
- File access permission control

## 🤝 Contributing Guide

### Development Process
1. Fork the project
2. Create feature branch
3. Submit code changes
4. Create Pull Request

### Code Standards
- Follow PEP 8 coding standards
- Add necessary comments and documentation
- Write unit tests

## 📄 License

This project is licensed under the MIT License. For details, please refer to the [LICENSE](LICENSE) file.

## 📞 Support & Contact

For questions or suggestions, please contact through:
- Submit Issues
- Send emails
- Participate in discussions

## 🔄 Changelog

### v1.0.0
- Initial version release
- Basic functionality implementation
- Documentation completion

---

**Note**: This project is under active development, and features may change. Please follow the latest updates.
