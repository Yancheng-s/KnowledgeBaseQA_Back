from typing import List
import faiss
import numpy as np
from langchain.schema import Document
from src.pojo.KBSconstruction_pojo import KBSconstruction_pojo
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import DashScopeEmbeddings
import traceback

embeddings = DashScopeEmbeddings(
    model="text-embedding-v2",
    dashscope_api_key="your-key"
)

knowledge_cache = {}

def search_multiple_kbs(kon_names: List[str], query: str, top_k: int = 5) -> List[Document]:
    all_docs = []
    for name in kon_names:
        # 检查缓存
        if name in knowledge_cache:
            vs = knowledge_cache[name]
        else:
            entry = KBSconstruction_pojo.query.filter_by(kon_name=name).first()
            if not entry or not entry.pkl_index_data or not entry.faiss_index_data:
                continue

            # 反序列化并缓存
            try:
                pkl_data = entry.pkl_index_data
                if isinstance(pkl_data, str):
                    pkl_data = pkl_data.encode('latin1')

                faiss_data = entry.faiss_index_data
                if isinstance(faiss_data, str):
                    faiss_data = faiss_data.encode('latin1')

                index = faiss.deserialize_index(np.frombuffer(faiss_data, dtype=np.uint8))
                vs = FAISS.deserialize_from_bytes(pkl_data, embeddings, allow_dangerous_deserialization=True)
                vs.index = index

                # 存入缓存
                knowledge_cache[name] = vs

            except Exception as e:
                print(f"🔥 加载知识库 {name} 出错: {str(e)}")
                continue

        # 搜索
        docs = vs.similarity_search(query, k=top_k)
        all_docs.extend(docs)

    # 去重逻辑
    seen = set()
    unique = []
    for d in all_docs:
        if d.page_content not in seen:
            seen.add(d.page_content)
            unique.append(d)
    return unique[:top_k]
