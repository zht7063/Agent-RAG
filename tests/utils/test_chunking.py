"""
测试 chunking 模块
"""

import pytest
from pathlib import Path
from pypdf import PdfReader

from src.utils.helpers.chunking import (
    ChunkConfig,
    get_chunk_config,
    smart_chunk,
    chunk_by_paragraphs,
    merge_small_chunks,
    add_chunk_metadata
)


class TestChunkConfig:
    """测试 ChunkConfig 数据类"""
    
    def test_chunk_config_default(self):
        """测试默认配置"""
        config = ChunkConfig()
        assert config.chunk_size == 1000
        assert config.chunk_overlap == 200
        assert config.separators == ["\n\n", "\n", " ", ""]
        assert config.length_function == "char"
    
    def test_chunk_config_custom(self):
        """测试自定义配置"""
        config = ChunkConfig(
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n\n", "\n"]
        )
        assert config.chunk_size == 500
        assert config.chunk_overlap == 100
        assert config.separators == ["\n\n", "\n"]


class TestGetChunkConfig:
    """测试 get_chunk_config 函数"""
    
    def test_get_pdf_config(self):
        """测试获取 PDF 配置"""
        config = get_chunk_config("pdf")
        assert config.chunk_size == 1000
        assert config.chunk_overlap == 200
        assert isinstance(config, ChunkConfig)
    
    def test_get_html_config(self):
        """测试获取 HTML 配置"""
        config = get_chunk_config("html")
        assert config.chunk_size == 800
        assert config.chunk_overlap == 150
        assert isinstance(config, ChunkConfig)
    
    def test_get_default_config(self):
        """测试获取默认配置"""
        config = get_chunk_config("default")
        assert config.chunk_size == 1000
        assert config.chunk_overlap == 200
    
    def test_get_unknown_type_returns_default(self):
        """测试未知类型返回默认配置"""
        config = get_chunk_config("unknown")
        assert config.chunk_size == 1000
        assert config.chunk_overlap == 200


class TestSmartChunk:
    """测试 smart_chunk 函数"""
    
    def test_smart_chunk_basic(self):
        """测试基本分块功能"""
        text = "这是第一段。\n\n这是第二段。\n\n这是第三段。"
        chunks = smart_chunk(text)
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, dict) for chunk in chunks)
        assert all("content" in chunk for chunk in chunks)
        assert all("start" in chunk for chunk in chunks)
        assert all("end" in chunk for chunk in chunks)
        assert all("metadata" in chunk for chunk in chunks)
    
    def test_smart_chunk_with_config(self):
        """测试使用自定义配置分块"""
        text = "A" * 2000  # 2000 个字符
        config = ChunkConfig(chunk_size=500, chunk_overlap=50)
        chunks = smart_chunk(text, config)
        
        # 应该被分成多块
        assert len(chunks) > 1
        # 每块大小不应超过 chunk_size
        assert all(len(chunk["content"]) <= 500 for chunk in chunks)
    
    def test_smart_chunk_short_text(self):
        """测试短文本分块"""
        text = "这是一个短文本。"
        chunks = smart_chunk(text)
        
        # 短文本应该只有一块
        assert len(chunks) == 1
        assert chunks[0]["content"] == text
        assert chunks[0]["metadata"]["chunk_index"] == 0
    
    def test_smart_chunk_metadata(self):
        """测试分块元数据"""
        text = "段落一。\n\n段落二。\n\n段落三。"
        chunks = smart_chunk(text)
        
        for idx, chunk in enumerate(chunks):
            assert chunk["metadata"]["chunk_index"] == idx
            assert "chunk_size" in chunk["metadata"]
            assert chunk["metadata"]["chunk_size"] == len(chunk["content"])


class TestChunkByParagraphs:
    """测试 chunk_by_paragraphs 函数"""
    
    def test_chunk_by_paragraphs_basic(self):
        """测试基本段落分块"""
        text = "段落1\n\n段落2\n\n段落3\n\n段落4\n\n段落5"
        chunks = chunk_by_paragraphs(text, max_paragraphs=2)
        
        assert len(chunks) == 3  # 5个段落，每2个一组，应该有3组
        assert "段落1" in chunks[0]
        assert "段落2" in chunks[0]
    
    def test_chunk_by_paragraphs_single(self):
        """测试单段落分块"""
        text = "只有一个段落"
        chunks = chunk_by_paragraphs(text, max_paragraphs=3)
        
        assert len(chunks) == 1
        assert chunks[0] == "只有一个段落"
    
    def test_chunk_by_paragraphs_empty(self):
        """测试空文本"""
        text = ""
        chunks = chunk_by_paragraphs(text)
        
        assert len(chunks) == 0


class TestMergeSmallChunks:
    """测试 merge_small_chunks 函数"""
    
    def test_merge_small_chunks_basic(self):
        """测试基本合并功能"""
        chunks = ["小块1", "小块2", "这是一个足够大的分块内容，超过了最小大小限制"]
        merged = merge_small_chunks(chunks, min_size=20)
        
        # 前两个小块应该被合并
        assert len(merged) < len(chunks)
    
    def test_merge_small_chunks_all_large(self):
        """测试所有块都足够大"""
        chunks = ["这是一个足够大的分块" * 10, "这也是一个足够大的分块" * 10]
        merged = merge_small_chunks(chunks, min_size=50)
        
        # 不应该合并
        assert len(merged) == len(chunks)
    
    def test_merge_small_chunks_empty(self):
        """测试空列表"""
        chunks = []
        merged = merge_small_chunks(chunks)
        
        assert len(merged) == 0
    
    def test_merge_small_chunks_single(self):
        """测试单个分块"""
        chunks = ["单个分块"]
        merged = merge_small_chunks(chunks, min_size=100)
        
        assert len(merged) == 1


class TestAddChunkMetadata:
    """测试 add_chunk_metadata 函数"""
    
    def test_add_chunk_metadata_basic(self):
        """测试基本元数据添加"""
        chunks = ["分块1", "分块2", "分块3"]
        result = add_chunk_metadata(chunks, "test_source.pdf")
        
        assert len(result) == len(chunks)
        assert all(isinstance(item, dict) for item in result)
        assert all("content" in item for item in result)
        assert all("metadata" in item for item in result)
    
    def test_add_chunk_metadata_source(self):
        """测试来源信息"""
        chunks = ["分块内容"]
        source = "document.pdf"
        result = add_chunk_metadata(chunks, source)
        
        assert result[0]["metadata"]["source"] == source
    
    def test_add_chunk_metadata_indices(self):
        """测试分块索引"""
        chunks = ["A", "B", "C"]
        result = add_chunk_metadata(chunks, "test")
        
        for idx, item in enumerate(result):
            assert item["metadata"]["chunk_index"] == idx
    
    def test_add_chunk_metadata_empty(self):
        """测试空列表"""
        chunks = []
        result = add_chunk_metadata(chunks, "test")
        
        assert len(result) == 0


class TestWithPDF:
    """使用真实 PDF 文件测试"""
    
    @pytest.fixture
    def pdf_text(self):
        """加载测试 PDF 文件内容"""
        pdf_path = Path("assets/pdf/xianfa.pdf")
        
        if not pdf_path.exists():
            pytest.skip(f"测试 PDF 文件不存在: {pdf_path}")
        
        reader = PdfReader(str(pdf_path))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        return text
    
    def test_chunk_pdf_content(self, pdf_text):
        """测试对 PDF 内容进行分块"""
        config = get_chunk_config("pdf")
        chunks = smart_chunk(pdf_text, config)
        
        # 验证分块结果
        assert len(chunks) > 0
        assert all(isinstance(chunk, dict) for chunk in chunks)
        
        # 验证分块大小
        for chunk in chunks:
            # 由于有 overlap，某些块可能略大于 chunk_size
            assert len(chunk["content"]) <= config.chunk_size + config.chunk_overlap
        
        # 验证元数据
        assert chunks[0]["metadata"]["chunk_index"] == 0
        if len(chunks) > 1:
            assert chunks[1]["metadata"]["chunk_index"] == 1
    
    def test_chunk_pdf_with_merge(self, pdf_text):
        """测试对 PDF 内容分块后合并小块"""
        config = ChunkConfig(chunk_size=100, chunk_overlap=20)
        chunks = smart_chunk(pdf_text, config)
        
        # 提取纯文本
        text_chunks = [chunk["content"] for chunk in chunks]
        
        # 合并小块
        merged = merge_small_chunks(text_chunks, min_size=80)
        
        # 合并后的块数应该减少
        assert len(merged) <= len(text_chunks)
    
    def test_chunk_pdf_with_metadata(self, pdf_text):
        """测试为 PDF 分块添加元数据"""
        config = get_chunk_config("pdf")
        chunks = smart_chunk(pdf_text, config)
        
        # 提取纯文本
        text_chunks = [chunk["content"] for chunk in chunks[:5]]  # 只取前5块测试
        
        # 添加元数据
        result = add_chunk_metadata(text_chunks, "xianfa.pdf")
        
        assert len(result) == len(text_chunks)
        assert all(r["metadata"]["source"] == "xianfa.pdf" for r in result)

