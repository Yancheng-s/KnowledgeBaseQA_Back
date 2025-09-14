from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import FAISS
import logging
import os


def vectorize_documents(documents, kon_name, emb_model):
    try:
        # 支持的阿里云Embedding模型
        supported_models = {
            "text-embedding-v1": "embedding-v1",
            "text-embedding-v2": "embedding-v2",
            "text-embedding-async-001": "embedding-async"
        }

        # 根据选择的模型设置参数
        if emb_model in supported_models:
            model_name = supported_models[emb_model]
        else:
            # 默认使用 text-embedding-v2（推荐）
            model_name = "text-embedding-v2"

        print(f"开始创建Embeddings对象，使用模型: {model_name}")

        # 创建Embeddings对象
        embeddings = DashScopeEmbeddings(
            model=model_name,
            dashscope_api_key="sk-c9b8659683a541bfaa8580448ca67766"
        )

        print(f"开始向量化 {len(documents)} 个文档")

        # 检查文档是否为空
        if not documents:
            raise ValueError("没有文档需要向量化")

        # 检查文档内容
        for i, doc in enumerate(documents):
            if not hasattr(doc, 'page_content') or not doc.page_content:
                logging.warning(f"文档 {i} 内容为空")

        vectorstore = FAISS.from_documents(documents, embeddings)

        # 确保目录存在
        vectorstore_dir = f"./vectorstores/{kon_name}"
        os.makedirs(os.path.dirname(vectorstore_dir), exist_ok=True)

        print(f"保存向量库到: {vectorstore_dir}")
        vectorstore.save_local(vectorstore_dir)

        print("向量化完成")
        return vectorstore

    except Exception as e:
        logging.error(f"向量化文档失败: {str(e)}", exc_info=True)
        raise Exception(f"向量化文档失败: {str(e)}")
