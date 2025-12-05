"""
datasource 模块 - 数据源服务

提供多种数据源的向量化存储和检索能力：

1. BaseVectorStore
   - 向量存储抽象基类
   - 统一的检索接口
   - 共享向量存储后端

2. PDFVectorStore
   - PDF 文档解析和分块
   - 向量化存储和检索
   - 元数据管理

3. HTMLVectorStore
   - 网页内容抓取和解析
   - 正文提取和清洗
   - 向量化存储

4. SQLVectorStore
   - 数据库 Schema 语义化
   - 表结构和字段描述向量化
   - 支持 NL2SQL 的语义匹配
"""

from .BaseVectorStore import BaseVectorStore
from .PDFVectorStore import PDFVectorStore
from .HTMLVectorStore import HTMLVectorStore
from .SQLVectorStore import SQLVectorStore

__all__ = [
    "BaseVectorStore",
    "PDFVectorStore",
    "HTMLVectorStore",
    "SQLVectorStore",
]

