# 数据库脚本说明

本目录包含用于管理和查看数据库的实用脚本。

## 📁 脚本列表

### 1. `seed_database.py` - 数据库填充脚本

生成包含丰富示例数据的演示数据库，用于开发测试和功能演示。

**功能：**
- 创建 30 篇经典 AI/ML 论文数据（Transformer、BERT、GPT-3、RAG、ReAct、CLIP、Stable Diffusion 等）
- 组织论文到 15 个主题合集（涵盖 NLP、CV、多模态、训练优化、安全对齐等领域）
- 为论文添加 24 条笔记（重点标注、评论、问题）
- 创建 12 个实验记录（不同状态：已完成、进行中、计划中）
- 记录 15 条研究灵感（不同优先级）

**使用方式：**

```bash
# 生成演示数据库
python scripts/seed_database.py

# 或使用 uv
uv run python scripts/seed_database.py
```

**输出：**
- 数据库文件：`data/scholar_demo.db`
- 包含完整的表结构和示例数据

---

### 2. `view_database.py` - 数据库查看脚本

查看和展示数据库中的所有数据，验证数据填充结果。

**功能：**
- 显示数据统计信息
- 列出所有论文
- 展示合集及其包含的论文
- 查看笔记内容（按类型分组）
- 显示实验记录（按状态分组）
- 查看研究灵感（按优先级分组）

**使用方式：**

```bash
# 查看默认数据库（data/scholar_demo.db）
python scripts/view_database.py

# 查看指定数据库
python scripts/view_database.py path/to/database.db

# 使用 uv
uv run python scripts/view_database.py
```

**输出示例：**

```
📊 数据总览:
  论文数量:   30 篇
  合集数量:   15 个
  笔记数量:   24 条
  实验数量:   12 个
  灵感数量:   15 条
```

---

## 🚀 快速开始

### 步骤 1：生成演示数据库

```bash
cd d:\projects\agenticRAG
uv run python scripts/seed_database.py
```

### 步骤 2：查看数据

```bash
uv run python scripts/view_database.py
```

### 步骤 3：在代码中使用

```python
from src.services.database.connection import DatabaseConnection
from src.services.database.repository import PaperRepository

# 连接数据库
db = DatabaseConnection("data/scholar_demo.db")
db.connect()

# 使用 Repository
paper_repo = PaperRepository(db)

# 查询论文
papers = paper_repo.search_by_keywords("transformer")
for paper in papers:
    print(f"{paper.title} - {paper.authors}")

# 关闭连接
db.close()
```

---

## 📊 示例数据概览

### 论文列表（30 篇）

涵盖 AI/ML 多个重要领域：

**NLP 与大语言模型（15 篇）：**
- Attention Is All You Need、BERT、GPT-3、LLaMA、GPT-1、T5
- InstructGPT (RLHF)、LoRA、Chain-of-Thought、ReAct
- Toolformer、Vicuna、Self-Instruct、LangChain、Scaling Laws

**计算机视觉（9 篇）：**
- ResNet、GAN、DenseNet、EfficientNet、Vision Transformer
- YOLO、Segment Anything (SAM)

**多模态与生成（6 篇）：**
- CLIP、Diffusion Models、Stable Diffusion、Flamingo

**RAG 与知识检索（3 篇）：**
- RAG、RAG Survey、GraphRAG

**AI 安全（1 篇）：**
- Constitutional AI

### 合集分类（15 个）

- **NLP 基础**：Transformer 架构、大语言模型、开源模型生态
- **模型优化**：训练与优化、指令微调与对齐、参数高效微调
- **应用与工具**：RAG、AI Agent、工具使用与框架
- **计算机视觉**：CV 经典、CV 架构、目标检测与分割、图像生成
- **跨领域**：多模态学习、AI 安全与对齐

### 研究笔记（24 条）

- 13 条重点标注
- 8 条评论
- 3 条问题

### 实验记录（12 个）

- 5 个已完成：BERT 微调、RAG 检索、LoRA 微调、CLIP 分类、Stable Diffusion 优化
- 3 个进行中：Transformer 可视化、SAM Prompt、GPT-3 Few-shot
- 4 个计划中：多 Agent 协同、ViT 数据效率、Constitutional AI、GraphRAG

### 研究灵感（15 条）

- 6 个高优先级：多模态 RAG、自反思 Agent、模型规模预测、混合 PEFT、工具学习、Agentic 工作流
- 6 个中优先级：论文引用图谱、跨语言迁移、视觉-语言迁移、扩散模型加速、联邦学习
- 3 个低优先级：领域文献综述、可解释注意力、模型压缩蒸馏

---

## 🔧 注意事项

1. **数据库路径**：
   - 默认生成在 `data/scholar_demo.db`
   - 如果文件已存在，脚本会提示是否覆盖

2. **依赖要求**：
   - 需要安装项目依赖：`uv sync`
   - 确保数据库 Schema 正常初始化

3. **数据完整性**：
   - 脚本使用事务确保数据一致性
   - 如果出现错误，数据会自动回滚

4. **测试隔离**：
   - 测试使用临时数据库，不会影响演示数据库
   - 演示数据库专用于开发和演示场景

---

## 💡 扩展建议

### 添加自定义数据

修改 `seed_database.py` 中的数据定义：

```python
SAMPLE_PAPERS = [
    {
        "title": "Your Paper Title",
        "authors": "Author Names",
        "abstract": "Paper abstract...",
        "keywords": "keyword1, keyword2",
        "publish_date": "2024-01-01",
        "venue": "Conference/Journal",
        "doi": "10.xxx/xxx",
        "url": "https://...",
    },
    # 添加更多论文...
]
```

### 创建自定义查看脚本

参考 `view_database.py` 创建自定义的数据展示逻辑：

```python
def view_custom_query(db):
    """自定义查询示例"""
    paper_repo = PaperRepository(db)
    
    # 查找最近发表的论文
    recent_papers = paper_repo.get_all(limit=5)
    
    for paper in recent_papers:
        print(f"{paper.title} ({paper.publish_date})")
```

---

## 📚 相关文档

- [数据库设计文档](../README.md#数据存储与管理)
- [测试文档](../tests/README.md)
- [API 文档](../docs/api.md)

---

## ❓ 常见问题

**Q: 数据库文件在哪里？**  
A: 默认在 `data/scholar_demo.db`，可以在脚本中修改路径。

**Q: 如何重置数据库？**  
A: 删除数据库文件后重新运行 `seed_database.py`，或者在提示时选择覆盖。

**Q: 可以在生产环境使用吗？**  
A: 这是演示数据库，仅用于开发测试。生产环境应使用 `data/scholar.db` 并导入真实数据。

**Q: 如何导入 PDF 文件？**  
A: 当前脚本只创建元数据。PDF 处理功能需要使用 `PDFVectorStore` 服务（开发中）。

