"""
测试 BaseVectorStore 抽象基类
"""

import pytest
from pathlib import Path
from typing import List, Any

from langchain_core.documents import Document

from src.services.datasource.BaseVectorStore import BaseVectorStore


class MockVectorStore(BaseVectorStore):
    """用于测试的具体实现类（Mock）"""
    
    def load_and_split(self, source: Any) -> List[Document]:
        """测试实现：直接返回测试文档"""
        if isinstance(source, str):
            return [
                Document(
                    page_content=f"测试文档内容 {i}",
                    metadata={
                        "source_type": "test",
                        "source": source,
                        "chunk_index": i,
                        "doc_id": 1
                    }
                )
                for i in range(3)
            ]
        return []


class TestBaseVectorStore:
    """测试 BaseVectorStore 基类功能"""
    
    @pytest.fixture
    def vector_store(self, tmp_path):
        """创建测试用的向量存储实例"""
        persist_dir = str(tmp_path / "test_vectorstore")
        store = MockVectorStore(
            persist_directory=persist_dir,
            collection_name="test_collection"
        )
        yield store
        
        # 清理
        try:
            store.clear_collection()
        except:
            pass
    
    def test_initialization(self, vector_store):
        """测试初始化"""
        assert vector_store.persist_directory is not None
        assert vector_store.collection_name == "test_collection"
        assert vector_store._embeddings is None  # 懒加载，未初始化
        assert vector_store._vector_store is None
    
    def test_embeddings_lazy_loading(self, vector_store):
        """测试 Embeddings 懒加载"""
        # 首次访问触发创建
        embeddings = vector_store.embeddings
        assert embeddings is not None
        assert vector_store._embeddings is not None
        
        # 再次访问返回同一实例
        embeddings2 = vector_store.embeddings
        assert embeddings is embeddings2
    
    def test_vector_store_lazy_loading(self, vector_store):
        """测试 VectorStore 懒加载"""
        # 首次访问触发创建
        vs = vector_store.vector_store
        assert vs is not None
        assert vector_store._vector_store is not None
        
        # 再次访问返回同一实例
        vs2 = vector_store.vector_store
        assert vs is vs2
    
    def test_load_and_split_abstract(self):
        """测试抽象方法必须由子类实现"""
        # 不能直接实例化抽象类
        with pytest.raises(TypeError):
            BaseVectorStore()
    
    def test_add_documents(self, vector_store):
        """测试添加文档"""
        documents = vector_store.load_and_split("test_source")
        assert len(documents) == 3
        
        ids = vector_store.add_documents(documents)
        assert len(ids) == 3
        assert all(isinstance(id, str) for id in ids)
    
    def test_add_empty_documents(self, vector_store):
        """测试添加空文档列表"""
        ids = vector_store.add_documents([])
        assert len(ids) == 0
    
    def test_search(self, vector_store):
        """测试语义检索"""
        # 先添加文档
        documents = vector_store.load_and_split("test_search")
        vector_store.add_documents(documents)
        
        # 检索
        results = vector_store.search("测试", k=2)
        assert len(results) <= 2
        assert all(isinstance(doc, Document) for doc in results)
    
    def test_search_with_score(self, vector_store):
        """测试带分数的检索"""
        # 添加文档
        documents = vector_store.load_and_split("test_score")
        vector_store.add_documents(documents)
        
        # 检索
        results = vector_store.search_with_score("测试", k=2)
        assert len(results) <= 2
        
        for doc, score in results:
            assert isinstance(doc, Document)
            assert isinstance(score, float)
            assert score >= 0  # 相似度分数应该非负
    
    def test_search_with_filter(self, vector_store):
        """测试带过滤条件的检索"""
        # 添加不同来源的文档
        docs1 = [
            Document(
                page_content="来源A的内容",
                metadata={
                    "source_type": "test",
                    "source": "source_a",
                    "chunk_index": 0
                }
            )
        ]
        docs2 = [
            Document(
                page_content="来源B的内容",
                metadata={
                    "source_type": "test",
                    "source": "source_b",
                    "chunk_index": 0
                }
            )
        ]
        
        vector_store.add_documents(docs1)
        vector_store.add_documents(docs2)
        
        # 按来源过滤检索
        results = vector_store.search(
            "内容",
            k=5,
            filter={"source": "source_a"}
        )
        
        assert len(results) >= 1
        # 验证返回的都是 source_a
        for doc in results:
            assert doc.metadata.get("source") == "source_a"
    
    def test_mmr_search(self, vector_store):
        """测试 MMR 检索"""
        # 添加文档
        documents = vector_store.load_and_split("test_mmr")
        vector_store.add_documents(documents)
        
        # MMR 检索
        results = vector_store.mmr_search("测试", k=2, lambda_mult=0.7)
        assert len(results) <= 2
        assert all(isinstance(doc, Document) for doc in results)
    
    def test_get_document_count(self, vector_store):
        """测试获取文档数量"""
        # 初始应该为 0
        count = vector_store.get_document_count()
        assert count == 0
        
        # 添加文档后数量增加
        documents = vector_store.load_and_split("test_count")
        vector_store.add_documents(documents)
        
        count = vector_store.get_document_count()
        assert count == 3
    
    def test_validate_metadata(self, vector_store):
        """测试元数据验证"""
        # 完整的元数据
        valid_metadata = {
            "source_type": "test",
            "source": "test.txt",
            "chunk_index": 0
        }
        assert vector_store._validate_metadata(valid_metadata) is True
        
        # 缺少字段的元数据
        invalid_metadata = {
            "source_type": "test"
        }
        assert vector_store._validate_metadata(invalid_metadata) is False
    
    def test_add_timestamp(self, vector_store):
        """测试添加时间戳"""
        metadata = {"source_type": "test"}
        
        result = vector_store._add_timestamp(metadata)
        assert "created_at" in result
        assert isinstance(result["created_at"], str)
        
        # 如果已有时间戳，不应该覆盖
        original_time = "2024-01-01T00:00:00"
        metadata_with_time = {
            "source_type": "test",
            "created_at": original_time
        }
        result = vector_store._add_timestamp(metadata_with_time)
        assert result["created_at"] == original_time
    
    def test_clear_collection(self, vector_store):
        """测试清空 collection"""
        # 添加文档
        documents = vector_store.load_and_split("test_clear")
        vector_store.add_documents(documents)
        
        # 确认有文档
        count = vector_store.get_document_count()
        assert count > 0
        
        # 清空
        success = vector_store.clear_collection()
        assert success is True
        
        # 确认已清空
        count = vector_store.get_document_count()
        assert count == 0


class TestVectorStoreIntegration:
    """集成测试"""
    
    @pytest.fixture
    def vector_store(self, tmp_path):
        """创建测试用向量存储"""
        persist_dir = str(tmp_path / "integration_test")
        store = MockVectorStore(
            persist_directory=persist_dir,
            collection_name="integration_test"
        )
        yield store
        
        try:
            store.clear_collection()
        except:
            pass
    
    def test_full_workflow(self, vector_store):
        """测试完整工作流：添加、检索、删除"""
        # 1. 加载和分块
        documents = vector_store.load_and_split("workflow_test")
        assert len(documents) == 3
        
        # 2. 添加文档
        ids = vector_store.add_documents(documents)
        assert len(ids) == 3
        
        # 3. 检索
        results = vector_store.search("测试", k=2)
        assert len(results) > 0
        
        # 4. 带分数检索
        scored_results = vector_store.search_with_score("测试", k=2)
        assert len(scored_results) > 0
        
        # 5. 获取数量
        count = vector_store.get_document_count()
        assert count == 3
        
        # 6. 清空
        vector_store.clear_collection()
        count = vector_store.get_document_count()
        assert count == 0

