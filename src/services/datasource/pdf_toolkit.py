"""
PDF 处理工具包

# 功能说明

该工具包提供对 PDF 加载、和分块功能，输出结果可以直接添加到向量存储库中。

# 调用方法

1. 构建 PDFToolkit 实例
2. 对于每个 pdf 文件（路径），调用 add_pdf 方法

该工具包在调用 add_pdf 之后，将会返回分块的 splits 列表，可以直接添加到向量存储库中。

"""

from dataclasses import dataclass
from typing import List
from langchain_core.documents import Document
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger
from abc_toolkit import BaseToolkit


class PDFToolkit(BaseToolkit):
    """ PDF 处理工具包 """

    def __init__(self):
        self.pdf_loader = PyPDFLoader()
        self.pdf_splitter = RecursiveCharacterTextSplitter()

    def _load_pdf(self, pdf_path: Path) -> List[Document]:
        """ 加载 PDF 文件 """
        loader = PyPDFLoader(pdf_path)
        docs =  loader.load()
        logger.info(f"PDF file {pdf_path} loaded, length: {len(docs)}")
        return docs

    def _split_pdf(self, docs: List[Document]) -> List[Document]:
        """ 分块 PDF 文件 """
        splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            chunk_overlap = 200,
            add_start_index = True,
        )
        splits = splitter.split_documents(docs)
        logger.info(f"PDF docs splitted, length: {len(splits)}")
        return splits

    def get_splits(self, pdf_path: Path) -> List[str]:
        """ 获取 PDF 文件的分块结果 """
        docs = self._load_pdf(pdf_path)
        splits = self._split_pdf(docs)
        return splits
