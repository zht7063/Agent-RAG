"""
Chunking - 文档分块工具

提供智能文档分块功能：

1. 分块策略
   - 基于字符数的分块
   - 基于 token 数的分块
   - 基于语义边界的分块

2. 分块配置
   - chunk_size: 分块大小
   - chunk_overlap: 重叠大小
   - separators: 分隔符列表

3. 语义分块
   - 识别段落边界
   - 识别章节边界
   - 保持上下文完整性

4. 元数据保留
   - 记录原始位置
   - 记录页码信息
   - 记录章节标题
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from langchain_text_splitters import RecursiveCharacterTextSplitter


@dataclass
class ChunkConfig:
    """分块配置"""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    separators: List[str] = None
    length_function: str = "char"  # "char" or "token"
    
    def __post_init__(self):
        if self.separators is None:
            self.separators = ["\n\n", "\n", " ", ""]


def get_chunk_config(doc_type: str = "default") -> ChunkConfig:
    """
    获取分块配置
    
    根据文档类型返回合适的分块配置。
    
    Args:
        doc_type: 文档类型（"pdf", "html", "default"）
        
    Returns:
        分块配置对象
    """
    configs = {
        "pdf": ChunkConfig(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        ),
        "html": ChunkConfig(
            chunk_size=800,
            chunk_overlap=150,
            separators=["\n\n", "\n", " ", ""]
        ),
        "default": ChunkConfig(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
    }
    
    return configs.get(doc_type, configs["default"])


def smart_chunk(text: str, config: ChunkConfig = None) -> List[Dict]:
    """
    智能分块
    
    根据配置将文本分割为多个块，保持语义完整性。
    
    Args:
        text: 输入文本
        config: 分块配置
        
    Returns:
        分块结果列表，每项包含 content, start, end, metadata 字段
    """
    if config is None:
        config = get_chunk_config()
    
    # 使用 LangChain 的 RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap,
        separators=config.separators,
        length_function=len
    )
    
    # 分块
    chunks = text_splitter.split_text(text)
    
    # 构建返回结果，包含位置信息
    results = []
    current_pos = 0
    
    for idx, chunk in enumerate(chunks):
        # 在原文中查找分块位置（估算）
        start = text.find(chunk, current_pos)
        if start == -1:
            start = current_pos
        end = start + len(chunk)
        
        results.append({
            "content": chunk,
            "start": start,
            "end": end,
            "metadata": {
                "chunk_index": idx,
                "chunk_size": len(chunk)
            }
        })
        
        current_pos = end
    
    return results


def chunk_by_sentences(text: str, max_sentences: int = 5) -> List[str]:
    """
    按句子数量分块
    
    Args:
        text: 输入文本
        max_sentences: 每块最大句子数
        
    Returns:
        分块列表
    """
    # 暂不实现，保留接口
    raise NotImplementedError("chunk_by_sentences 功能待实现")


def chunk_by_paragraphs(text: str, max_paragraphs: int = 3) -> List[str]:
    """
    按段落分块
    
    Args:
        text: 输入文本
        max_paragraphs: 每块最大段落数
        
    Returns:
        分块列表
    """
    # 简单的段落分块，基于 \n\n 分割
    paragraphs = text.split("\n\n")
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    
    chunks = []
    current_chunk = []
    
    for paragraph in paragraphs:
        current_chunk.append(paragraph)
        if len(current_chunk) >= max_paragraphs:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = []
    
    # 添加剩余段落
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
    
    return chunks


def find_semantic_boundaries(text: str) -> List[int]:
    """
    识别语义边界位置
    
    Args:
        text: 输入文本
        
    Returns:
        语义边界位置列表
    """
    # 暂不实现，保留接口
    raise NotImplementedError("find_semantic_boundaries 功能待实现")


def merge_small_chunks(chunks: List[str], min_size: int = 100) -> List[str]:
    """
    合并过小的分块
    
    将小于 min_size 的分块与相邻分块合并，以提高检索效果。
    
    Args:
        chunks: 分块列表
        min_size: 最小分块大小
        
    Returns:
        合并后的分块列表
    """
    if not chunks:
        return []
    
    merged = []
    current_chunk = chunks[0]
    
    for i in range(1, len(chunks)):
        if len(current_chunk) < min_size:
            # 当前块太小，与下一块合并
            current_chunk = current_chunk + " " + chunks[i]
        else:
            # 当前块足够大，保存并开始新块
            merged.append(current_chunk)
            current_chunk = chunks[i]
    
    # 添加最后一块
    merged.append(current_chunk)
    
    return merged


def add_chunk_metadata(chunks: List[str], source: str) -> List[Dict]:
    """
    为分块添加元数据
    
    Args:
        chunks: 分块列表
        source: 来源信息
        
    Returns:
        包含元数据的分块字典列表
    """
    results = []
    
    for idx, chunk in enumerate(chunks):
        results.append({
            "content": chunk,
            "metadata": {
                "source": source,
                "chunk_index": idx,
                "chunk_size": len(chunk)
            }
        })
    
    return results

