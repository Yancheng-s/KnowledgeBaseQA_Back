# src/utils/chunk_documents.py

from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
import re


def chunk_documents(documents, chunk_setting, chunk_size, chunk_overlap,
                    sentence_identifier):
    """
    对文档进行分块处理
    Args:
        documents: 文档列表
        chunk_setting: 切分规则（"default", "custom"）
        sentence_identifier: 切分规则（"按页面","按一级标题","按二级标题","按长度"）
        chunk_size: 每个chunk的目标token数，默认600
        chunk_overlap: chunk间的重叠token数，默认100
    Returns:
        分块后的文档列表
    """

    # 验证参数：确保chunk_overlap小于chunk_size
    if chunk_overlap >= chunk_size:
        # 如果overlap大于等于size，则将其设置为size的一半或一个较小的值
        chunk_overlap = chunk_size // 2 if chunk_size > 1 else 0

    if chunk_setting == "default":
        # 使用默认的递归字符切分器
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
    elif chunk_setting == "custom":
        # 根据分隔符类型选择不同的处理方式
        if sentence_identifier == "按页面":
            text_splitter = CharacterTextSplitter(
                separator="\f",
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
        elif sentence_identifier == "按一级标题":
            text_splitter = CharacterTextSplitter(
                separator="\n# ",
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
        elif sentence_identifier == "按二级标题":
            text_splitter = CharacterTextSplitter(
                separator="\n## ",
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
        else:
            # 按长度或其他自定义分隔符
            text_splitter = CharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
    else:
        raise ValueError(f"Unsupported chunk setting: {chunk_setting}")

    split_documents = text_splitter.split_documents(documents)
    return split_documents
