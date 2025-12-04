"""
Retrieval Worker - 检索代理

主要职责：
1. 文档向量检索
   - PDF 文档语义检索（调用 PDFVectorStore）
   - HTML 网页内容检索（调用 HTMLVectorStore）

2. 混合检索策略
   - 关键词检索 + 向量检索融合
   - 检索结果重排序 (Reranking)

3. Query 优化
   - Query Rewrite：长难查询改写优化
   - Query Expansion：查询扩展提升召回

4. 多页上下文关联
   - 支持跨页/跨文档的上下文关联检索
   - 返回检索结果及来源元数据
"""

