# lang-flow_3-d-digital-human_-back

This is a Flask-based backend project primarily used for building digital human applications. The project integrates functionalities such as document processing, vector storage, and model invocation, making it suitable for applications requiring large-scale text processing and interaction.

## Features

- **Document Processing**: Supports document loading, chunking, and vectorized storage.
- **Object Storage Service Integration**: Integrated with OSS file upload functionality, supporting both synchronous and asynchronous file uploads.
- **Model Invocation**: Supports invoking external model interfaces for conversation completion.
- **Modular Design**: Facilitates extension and maintenance through modular routing and functional components.

## Directory Structure

- `src/`: Core source code directory.
  - `file/`: Modules related to file processing.
  - `pojo/`: Data model definitions.
  - `route/`: Routing registration module.
  - `utils/`: Utility modules, including document chunking, vectorization, model invocation, etc.
- `database/`: Database configuration files.
- `vectorstores/`: Vector storage directory containing multiple index files.

## Installation and Execution

### Dependency Installation

Ensure Python 3.x and pip are installed, then execute:

```bash
pip install -r requirements.txt
```

### Starting the Service

Run `main.py` to start the Flask service:

```bash
python main.py
```

## Usage Instructions

1. **Document Processing**: Upload documents via the `/file` interface; the system will automatically perform chunking and vectorization.
2. **Model Invocation**: Invoke models for conversation completion via the `/agent` interface.
3. **Knowledge Base Construction**: Build a knowledge base via the `/kbs` interface and store it in the vector database.

## Contribution Guidelines

Code contributions and documentation improvements are welcome. Please follow these steps:

1. Fork the project.
2. Create a new branch.
3. Submit code changes.
4. Submit a Pull Request.

## License

This project is licensed under the MIT License. For details, please refer to the LICENSE file.