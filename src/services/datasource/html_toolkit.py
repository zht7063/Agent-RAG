"""
html 处理工具包

# 功能说明

1. 通过 url 获取 html 内容；
2. 对 html 内容进行清洗；
3. 对 html 内容进行分块。

最终输出 splits[Document] 列表，可以直接添加到向量存储库中。


# 依赖工具：

(uv add trafilatura)[https://github.com/adbar/trafilatura]

"""
from trafilatura import extract, ExtractionConfig
import requests
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from abc_toolkit import BaseToolkit


class HTMLToolkit(BaseToolkit)  :
    """ HTML 处理工具包 """
    def __init__(self):
        self.url = None

    def get_text_content(self, url: str) -> str | None:
        """ 获取 url 的 html 内容 """
        self.url = url
        html_text = self._get_response_text()
        text = self._extract_main_text(html_text)
        return text
    
    def _get_response_text(self, timeout: int = 10) -> str | None:
        """ 获取 url 的 html 内容 """
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }

        resp = requests.get(
            self.url, 
            headers = headers, 
            timeout = timeout
        )
        
        resp.raise_for_status()
        return resp.text
    
    def _extract_main_text(self, html_text: str, config: ExtractionConfig = None) -> str | None:
        """ 提取 html 内容中的主要文本 """
        if not html_text:
            return None
        
        if not config:
            config = ExtractionConfig(
                include_comments=False,
                include_tables=False,
                favor_recall=True,
                with_metadata=True,
            )

        text = extract(
            html_text, 
            config = config, 
            url = self.url
        )

        return text
    
    def get_splits(self, text: str) -> List[Document]:
        """ 对文本进行两阶段分块处理 """
        # 1. 按段落分割
        paragraphs = self._split_by_paragraphs(text)
        
        # 2. 处理短段落
        cleaned_paragraphs = self._merge_short_paragraphs(paragraphs, min_length=50)
        
        # 3. 创建段落级 Document 列表
        paragraph_docs = self._create_paragraph_documents(cleaned_paragraphs)
        
        # 4. 二次分块
        final_splits = self._split_documents(paragraph_docs)
        
        return final_splits
    
    def _split_by_paragraphs(self, text: str) -> List[str]:
        """ 按段落分割文本 """
        paragraphs = text.split("\n\n")
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        return paragraphs
    
    def _merge_short_paragraphs(self, paragraphs: List[str], min_length: int) -> List[str]:
        """ 合并过短的段落 """
        if not paragraphs:
            return []
        
        merged = []
        i = 0
        
        while i < len(paragraphs):
            current = paragraphs[i]
            
            if len(current) < min_length:
                # 如果当前段落过短
                if merged:
                    # 如果有前一个段落，合并到前一个
                    merged[-1] = merged[-1] + " " + current
                elif i + 1 < len(paragraphs):
                    # 如果没有前一个段落但有后一个，与后一个合并
                    current = current + " " + paragraphs[i + 1]
                    i += 1
                    merged.append(current)
                else:
                    # 如果只有这一个段落，保留它
                    merged.append(current)
            else:
                # 段落长度足够，直接添加
                merged.append(current)
            
            i += 1
        
        return merged
    
    def _create_paragraph_documents(self, paragraphs: List[str]) -> List[Document]:
        """ 为每个段落创建 Document 对象 """
        docs = []
        for idx, paragraph in enumerate(paragraphs):
            doc = Document(
                page_content=paragraph,
                metadata={
                    "source": self.url,
                    "paragraph_index": idx,
                    "type": "paragraph"
                }
            )
            docs.append(doc)
        return docs
    
    def _split_documents(self, docs: List[Document]) -> List[Document]:
        """ 使用 RecursiveCharacterTextSplitter 进行二次分块 """
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            add_start_index=True,
            separators=["\n\n", "\n", " ", ""]
        )
        splits = splitter.split_documents(docs)
        return splits

