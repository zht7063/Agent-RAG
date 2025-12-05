"""
工具包的抽象父类，用于统一定义工具包需要具有的功能。
"""
from abc import ABC, abstractmethod
from langchain_core.documents import Document
from typing import List


class BaseToolkit(ABC):
    @abstractmethod
    def get_splits(self) -> List[Document]:
        """
            返回 splits[Document] 列表.

            所有数据源工具包都必须实现该函数，通过统一返回 splits[Document] 列表，使其输出结果可以直接进行向量化并加入到向量存储中。
        """
        pass
