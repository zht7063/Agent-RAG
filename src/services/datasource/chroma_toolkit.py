"""
向量存储工具包

# 功能说明

该工具包提供向量存储相关的工具函数，包括：

1. 提供数据向量化方法；
2. 提供 Chroma 向量存储库；

# 注意：

这里只提供一个封装 chroma 的客户端，以便于在多个数据源的时候使用相同的向量存储库，本工具包不提供数据源加载和分块为 Document 对象列表的功能，具体实现请参考 `datasource` 中的其余模块。

"""

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dataclasses import dataclass
from typing import List


@dataclass
class vector_store_config:
    collection_name: str
    embedding_func: str
    presist_dir: str


class VectorStoreToolkit:
    """ 向量存储工具包 """

    def __init__(self, vector_store_config):
        self.chroma_client = Chroma(
            collection_name = vector_store_config.collection_name,
            embedding_function = vector_store_config.embedding_func,
            persist_directory = vector_store_config.presist_dir,
        )

    def add_documents(self, documents: List[Document]) -> List[str]:
        """ 添加文档到向量存储库 """
        ids = self.chroma_client.add_documents(documents)
        return ids

