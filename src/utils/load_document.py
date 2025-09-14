# src/utils/load_document.py
import os
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredWordDocumentLoader,
    CSVLoader
)
import pandas as pd


def load_document(file_path, excel_header_processing=False):
    _, ext = os.path.splitext(file_path)
    ext = ext.lower().strip()  # 去除可能的点号并转小写

    if ext == '.txt':
        loader = TextLoader(file_path, encoding='utf-8')  # 指定编码避免报错
    elif ext == '.pdf':
        loader = PyPDFLoader(file_path)
    elif ext == '.docx':
        loader = Docx2txtLoader(file_path)
    elif ext == '.doc':
        loader = UnstructuredWordDocumentLoader(file_path)
    elif ext in ['.xlsx', '.xls']:
        # 处Excel文件
        if excel_header_processing:
            # 如果需要处理表头，则使用自定义方法
            return load_excel_with_headers(file_path)
        else:
            # 否则使用默认方法
            loader = CSVLoader(file_path)
    elif ext == '.csv':
        # 处理CSV文件
        if excel_header_processing:
            # 如果需要处理表头，则使用自定义方法
            return load_csv_with_headers(file_path)
        else:
            # 否则使用默认方法
            loader = CSVLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    return loader.load()


def load_excel_with_headers(file_path):
    """
    加载Excel文件并将表头拼接到每一行内容中
    """
    try:
        # 读取Excel文件
        excel_file = pd.ExcelFile(file_path)
        documents = []

        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            headers = df.columns.tolist()

            # 将表头信息添加到每个数据行
            for _, row in df.iterrows():
                content_parts = []
                for i, value in enumerate(row):
                    if pd.notna(value):  # 只添加非空值
                        header = headers[i] if i < len(headers) else f"列{i}"
                        content_parts.append(f"{header}: {value}")

                if content_parts:  # 只有当有内容时才创建文档
                    content = "; ".join(content_parts)
                    documents.append(type('Document', (), {'page_content': content, 'metadata': {}})())

        return documents
    except Exception as e:
        raise ValueError(f"处理Excel文件失败: {str(e)}")


def load_csv_with_headers(file_path):
    """
    加载CSV文件并将表头拼接到每一行内容中
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path, encoding='utf-8')
        headers = df.columns.tolist()
        documents = []

        # 将表头信息添加到每个数据行
        for _, row in df.iterrows():
            content_parts = []
            for i, value in enumerate(row):
                if pd.notna(value):  # 只添加非空值
                    header = headers[i] if i < len(headers) else f"列{i}"
                    content_parts.append(f"{header}: {value}")

            if content_parts:  # 只有当有内容时才创建文档
                content = "; ".join(content_parts)
                documents.append(type('Document', (), {'page_content': content, 'metadata': {}})())

        return documents
    except Exception as e:
        raise ValueError(f"处理CSV文件失败: {str(e)}")
