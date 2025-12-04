"""
构建向量数据库
"""
from typing import List
# import subprocess
from pathlib import Path
from loguru import logger
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.settings import project_root


class VectorStore:

    def __init__(self, pdf_path: Path):
        self.vector_store = Chroma(
            collection_name = "pdf_collection",
            embedding_function = OpenAIEmbeddings(),
            # 指定存储路径后会自动进行持久化
            persist_directory = project_root() / "assets" / "vector_store"
        )

    def pdf2splits(self, pdf_path: Path) -> List[Document]:
        """ 加载 pdf 文件
        
        1. 使用 langchain_community.document_loaders import PyPDFLoader 加载 pdf 文件
        2. 使用 langchain_text_splitters.RecursiveCharacterTextSplitter 对文档进行分块

        """
        # 1. 使用 langchain_community.document_loaders import PyPDFLoader 加载 pdf 文件
        loader = PyPDFLoader(str(pdf_path))
        docs = loader.load()

        # 2. 使用 langchain_text_splitters.RecursiveCharacterTextSplitter 对文档进行分块
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            chunk_overlap = 200
        )
        splits = text_splitter.split_documents(docs)

        logger.info(f"分块后 splits 数量：{len(splits)}")

        # 3. 返回分块后的 Document 对象列表
        return splits
    
    def join_vector_store(self, splits: List[Document]) -> List[str]:
        """ 将分块后的 Document 对象列表加入向量数据库 """
        ids = self.vector_store.add_documents(splits)
        logger.info(f"加入向量数据库成功，文档 ID: {ids}")
        logger.info(f"向量数据库已自动持久化到: {project_root() / 'assets' / 'vector_store'}")
        return ids
    
    def search_vector_store(self, query: str) -> List[Document]:
        """ 在向量数据库中搜索相似的 Document 对象 """
        return self.vector_store.similarity_search(query)
        

def test_vector_store():
    pdf_path = project_root() / "assets" / "pdf" / "xianfa.pdf"
    
    # 检查 PDF 文件是否存在
    if not pdf_path.exists():
        logger.error(f"PDF 文件不存在: {pdf_path}")
        exit(1)
    
    logger.info(f"开始处理 PDF 文件: {pdf_path}")
    
    # 创建 VectorStore 实例
    vector_store = VectorStore(pdf_path)
    
    # 加载并分块 PDF
    logger.info("开始加载和分块 PDF 文件...")
    splits = vector_store.pdf2splits(pdf_path)
    
    # 将分块加入向量数据库
    logger.info("开始将文档加入向量数据库...")
    vector_store.join_vector_store(splits)
    
    # 测试检索功能
    test_queries = [
        "中华人民共和国宪法的主要内容是什么？",
        "公民的基本权利和义务有哪些？",
        "国家机构的组成和职责是什么？",
        "宪法的基本原则是什么？"
    ]
    
    logger.info("开始测试检索功能...")
    for query in test_queries:
        logger.info(f"\n查询: {query}")
        results = vector_store.search_vector_store(query)
        logger.info(f"检索到 {len(results)} 条相关文档")
        for i, doc in enumerate(results[:3], 1):  # 只显示前3条
            logger.info(f"结果 {i}: {doc.page_content[:200]}...")
    
    logger.info("测试完成！")
