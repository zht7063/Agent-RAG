# ScholarRAG - 科研文献智能助手

基于 Agentic RAG 架构的科研文献收集、学习与研究辅助系统。

---

# 项目功能设计

## 1. 整体架构：Master-Worker 协同模式

### 1.1 Master Agent（主控代理）

Master Agent 作为用户的直接交互入口，负责：

- **对话管理**：接收用户输入，理解用户意图，维护多轮对话上下文
- **任务规划**：分析用户需求的复杂度，将复杂任务拆解为可执行的子任务
- **Worker 调度**：根据任务类型选择合适的 Worker，支持串行或并行调度
- **答案整合**：汇总各 Worker 返回的信息，进行自反思（Self-reflection）
- **质量控制**：评估答案质量，若发现信息不足或存在幻觉，自动触发重检索或补充搜索

### 1.2 Worker Agent（工作代理）

专业化的 Worker 负责执行具体任务：

| Worker 类型 | 职责 | 触发场景 |
|------------|------|---------|
| **Retrieval Worker** | 文献检索、向量搜索、上下文召回 | 用户提问涉及已存储文献内容 |
| **SQL Worker** | 数据库查询、论文元数据检索、实验数据管理 | 需要结构化数据支持时 |
| **WebSearch Worker** | 网络搜索、论文信息获取、学术资源发现 | 本地知识库不足或需要最新信息时 |
| **Generation Worker** | 答案生成、文献综述、研究建议 | 需要生成总结性或创造性内容时 |

### 1.3 交互流程

```
用户提问 → Master 分析意图 → 选择 Worker(s) → Worker 执行任务
                ↑                                    ↓
                └──── 自反思/重检索 ←── Master 整合答案 ←──┘
                                            ↓
                                     答案满意 → 返回用户
```

---

## 2. 文献读取与理解

### 2.1 PDF 文档处理

- **文档解析**
  - 提取文档结构：标题、章节、段落、表格、图片说明
  - 识别论文元数据：标题、作者、摘要、关键词、发表时间、期刊/会议
  - 解析参考文献列表，建立引用关系

- **智能分块（Chunking）**
  - 基于语义边界的分块策略，避免上下文断裂
  - 保留章节层级信息，支持上下文关联检索
  - 支持自定义分块大小和重叠度

- **向量化存储**
  - 使用 Embedding 模型将文档块转换为向量
  - 存储向量及对应的文本块、元数据
  - 支持增量更新和去重

### 2.2 HTML/网页处理

- **URL 解析**
  - 支持用户指定 URL 进行内容抓取
  - 智能提取正文内容，过滤导航栏、广告等噪声
  - 保留文章结构和关键元素

- **内容存储**
  - 与 PDF 共享向量存储空间，支持跨来源检索
  - 记录来源 URL、抓取时间、内容摘要

### 2.3 Agentic RAG 检索

- **智能检索触发**
  - Master 自动判断用户问题是否需要文献支持
  - 根据问题类型选择检索策略：精确检索 / 模糊检索 / 多跳检索

- **混合检索策略**
  - 关键词检索 + 向量语义检索的融合
  - 支持 Query Rewrite 优化长难查询
  - 多源检索结果的去重与排序

- **上下文增强**
  - 检索结果附带来源信息（文档名、页码、章节）
  - 支持追溯答案依据，提供引用链接

---

## 3. 数据存储与管理

### 3.1 SQLite 数据库设计

数据库用于存储结构化的研究数据，主要包含以下模块：

- **论文元数据库（papers）**
  - 论文基本信息：标题、作者、摘要、关键词、发表时间
  - 来源信息：期刊/会议、DOI、URL
  - 本地关联：对应的 PDF 文件路径、向量索引 ID

- **文献合集（collections）**
  - 用户自定义的文献分组
  - 支持按研究主题、项目、时间等维度组织
  - 合集描述和标签

- **研究笔记（notes）**
  - 与论文关联的阅读笔记
  - 关键观点摘录和个人批注
  - 研究问题和待办事项

- **实验记录（experiments）**
  - 实验设计、参数、结果记录
  - 与论文的关联（方法来源、对比基准）
  - 时间线追踪

- **研究灵感（inspirations）**
  - 跨论文的关联发现
  - 研究方向建议
  - 待探索的问题

### 3.2 智能数据调用

- **语境感知**
  - 当用户讨论某个研究主题时，自动关联相关论文信息
  - 根据对话上下文推荐相关的实验记录或笔记

- **主动推荐**
  - 基于用户研究方向，推荐可能相关的论文
  - 发现论文间的方法关联、引用关系

- **NL2SQL**
  - 支持自然语言查询数据库
  - 示例："找出 2024 年关于 RAG 的所有论文" → 自动生成 SQL 查询

---

## 4. 网络信息检索

### 4.1 MCP 协议集成

通过 Model Context Protocol (MCP) 接入外部信息源：

- **学术搜索**
  - 搜索关键词获取相关论文列表
  - 获取论文基本信息（标题、作者、摘要、引用数）
  - 支持按时间、引用数、相关性排序

- **网页内容获取**
  - 抓取用户指定的论文页面或学术网站
  - 解析论文详情、补充材料链接
  - 获取最新学术动态

### 4.2 搜索增强

- **查询优化**
  - 根据用户问题自动生成搜索关键词
  - 支持学术术语扩展和同义词替换

- **结果整合**
  - 网络搜索结果与本地知识库的融合
  - 去重和质量评估
  - 标注信息来源（本地 / 网络）

---

## 5. 研究辅助功能

### 5.1 文献综述生成

- 基于检索到的多篇论文，生成结构化的文献综述
- 支持按主题、方法、时间线等维度组织
- 自动生成参考文献列表

### 5.2 研究问题探索

- 分析论文中的研究空白和未来方向
- 根据用户兴趣推荐潜在研究问题
- 跨论文的方法对比和创新点发现

### 5.3 实验管理

- 记录实验设计和参数配置
- 追踪实验结果和迭代历史
- 与论文方法的关联对比

---

# 项目结构设计与实现方案

## 1. 目录结构

```
agent-rag/
├── main.py                     # 应用入口
├── pyproject.toml              # 项目配置和依赖管理
├── README.md                   # 项目说明文档
│
├── config/                     # 配置文件目录
│   ├── __init__.py
│   └── settings.py             # 应用配置（API Key、模型参数、数据库路径等）
│
├── src/                        # 源代码目录
│   ├── agents/                 # Agent 实现
│   │   ├── __init__.py
│   │   ├── master.py           # Master Agent 主控代理
│   │   ├── worker_base.py      # Worker 基类
│   │   ├── worker_retrieval.py # 检索 Worker
│   │   ├── worker_sql.py       # SQL Worker
│   │   ├── worker_websearch.py # 网络搜索 Worker
│   │   └── worker_generation.py# 生成 Worker
│   │
│   ├── services/               # 服务层
│   │   ├── __init__.py
│   │   ├── datasource/         # 数据源服务
│   │   │   ├── __init__.py
│   │   │   ├── PDFVectorStore.py   # PDF 向量存储
│   │   │   ├── HTMLVectorStore.py  # HTML 向量存储
│   │   │   └── SQLVectorStore.py   # SQL 向量存储（Schema 语义化）
│   │   │
│   │   ├── database/           # 数据库服务
│   │   │   ├── __init__.py
│   │   │   ├── connection.py   # SQLite 连接管理（单例模式、事务、查询）
│   │   │   ├── schema.py       # 数据库 Schema 定义和版本管理
│   │   │   └── repository.py   # 数据访问层（Paper, Collection, Note, Experiment, Inspiration）
│   │   │
│   │   └── mcp/                # MCP 协议服务
│   │       ├── __init__.py
│   │       ├── MCPWebSearch.py # 网络搜索服务
│   │       ├── MCPFetch.py     # 网页抓取服务
│   │       └── MCPTime.py      # 时间服务
│   │
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       ├── tools/              # Agent 工具集
│       │   ├── __init__.py
│       │   ├── retrieval_tools.py  # 检索工具
│       │   ├── database_tools.py   # 数据库工具
│       │   └── search_tools.py     # 搜索工具
│       │
│       └── helpers/            # 辅助函数
│           ├── __init__.py
│           ├── text_processing.py  # 文本处理
│           ├── chunking.py         # 文档分块
│           └── logger.py           # 日志工具（基于 loguru）
│
├── tests/                      # 测试模块
│   ├── __init__.py
│   ├── conftest.py             # pytest 配置和共享 fixtures
│   └── database/               # 数据库测试
│       ├── __init__.py
│       ├── test_connection.py  # 连接管理测试
│       ├── test_schema.py      # Schema 管理测试
│       └── test_repository.py  # Repository CRUD 测试
│
├── data/                       # 数据目录
│   ├── vectorstore/            # 向量数据库存储
│   ├── scholar.db              # SQLite 数据库文件
│   └── documents/              # 原始文档存储（PDF、HTML 缓存）
│
└── assets/                     # 资源文件（配置模板等）
```

## 2. 技术栈

| 层级 | 技术选型 | 说明 |
|-----|---------|------|
| LLM 框架 | LangChain 1.x | Agent 构建、工具调用、Chain 编排 |
| 向量数据库 | Chroma / FAISS | 文档向量存储和检索 |
| 关系数据库 | SQLite3 | 结构化数据存储 |
| PDF 解析 | pypdf / pdfplumber | 文档内容提取 |
| Web 服务 | FastAPI | API 服务（可选） |
| MCP 协议 | langchain-mcp | 外部服务集成 |

## 3. 核心模块实现方案

### 3.1 Master Agent

```python
# src/agents/master.py 核心逻辑

class MasterAgent:
    """主控代理，负责用户交互和 Worker 协调"""
    
    def __init__(self):
        self.workers = {}           # Worker 注册表
        self.conversation_history = []  # 对话历史
        self.llm = None             # LLM 实例
    
    def process_query(self, user_input: str) -> str:
        """处理用户查询的主流程"""
        # 1. 意图分析
        intent = self._analyze_intent(user_input)
        
        # 2. 任务规划
        tasks = self._plan_tasks(intent, user_input)
        
        # 3. Worker 调度
        results = self._dispatch_workers(tasks)
        
        # 4. 答案整合
        answer = self._integrate_results(results, user_input)
        
        # 5. 自反思检查
        if self._needs_refinement(answer):
            return self._refine_answer(answer, user_input)
        
        return answer
```

### 3.2 Worker 基类

```python
# src/agents/worker_base.py

class BaseWorker:
    """Worker 基类，定义通用接口"""
    
    def __init__(self, name: str, tools: list):
        self.name = name
        self.tools = tools
        self.llm = None
    
    def execute(self, task: dict) -> dict:
        """执行任务并返回结构化结果"""
        raise NotImplementedError
    
    def format_result(self, raw_result) -> dict:
        """格式化执行结果"""
        return {
            "worker": self.name,
            "status": "success",
            "data": raw_result,
            "sources": []
        }
```

### 3.3 向量存储服务

```python
# src/services/datasource/PDFVectorStore.py 核心逻辑

class PDFVectorStore:
    """PDF 文档向量存储服务"""
    
    def __init__(self, persist_directory: str):
        self.vectorstore = None
        self.embeddings = None
    
    def add_document(self, pdf_path: str, metadata: dict = None):
        """添加 PDF 文档到向量库"""
        # 1. 解析 PDF
        # 2. 智能分块
        # 3. 向量化存储
        pass
    
    def search(self, query: str, k: int = 5) -> list:
        """语义检索"""
        pass
    
    def hybrid_search(self, query: str, k: int = 5) -> list:
        """混合检索（关键词 + 语义）"""
        pass
```

### 3.4 数据库 Schema

```sql
-- 论文元数据表
CREATE TABLE papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    authors TEXT,
    abstract TEXT,
    keywords TEXT,
    publish_date TEXT,
    venue TEXT,              -- 期刊/会议
    doi TEXT,
    url TEXT,
    pdf_path TEXT,           -- 本地 PDF 路径
    vector_ids TEXT,         -- 关联的向量索引 ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 文献合集表
CREATE TABLE collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 合集-论文关联表
CREATE TABLE collection_papers (
    collection_id INTEGER,
    paper_id INTEGER,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (collection_id, paper_id),
    FOREIGN KEY (collection_id) REFERENCES collections(id),
    FOREIGN KEY (paper_id) REFERENCES papers(id)
);

-- 研究笔记表
CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id INTEGER,
    content TEXT NOT NULL,
    note_type TEXT,          -- highlight, comment, question
    page_number INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers(id)
);

-- 实验记录表
CREATE TABLE experiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    parameters TEXT,         -- JSON 格式
    results TEXT,            -- JSON 格式
    related_papers TEXT,     -- 关联论文 ID 列表
    status TEXT,             -- planned, running, completed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 研究灵感表
CREATE TABLE inspirations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT,
    source_papers TEXT,      -- 灵感来源论文 ID
    priority TEXT,           -- high, medium, low
    status TEXT,             -- new, exploring, archived
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 4. 实现路线图

### Phase 1: 基础设施（1-2 周）

1. 完善 `config/settings.py` 配置管理
2. 实现 `PDFVectorStore` 和 `HTMLVectorStore`
3. 设计并初始化 SQLite 数据库 Schema
4. 实现基础的文档分块和向量化

### Phase 2: Worker 实现（2-3 周）

1. 实现 `BaseWorker` 基类和工具注册机制
2. 实现 `RetrievalWorker`（文献检索）
3. 实现 `SQLWorker`（数据库查询）
4. 实现 `WebSearchWorker`（MCP 网络搜索）
5. 实现 `GenerationWorker`（答案生成）

### Phase 3: Master Agent（1-2 周）

1. 实现意图分析和任务规划
2. 实现 Worker 调度机制
3. 实现结果整合和自反思
4. 实现多轮对话上下文管理

### Phase 4: 功能完善（2-3 周）

1. 实现混合检索策略
2. 实现 NL2SQL 功能
3. 完善论文元数据提取
4. 实现研究辅助功能（综述生成、灵感推荐）

### Phase 5: 应用集成（1 周）

1. CLI 交互入口
2. FastAPI 服务（可选）
3. 日志和错误处理完善

## 5. 设计原则

1. **分层解耦**：Agent 层 → Service 层 → Utils 层，职责清晰
2. **接口优先**：定义清晰的模块接口，便于扩展和测试
3. **配置集中**：所有配置统一管理，支持环境变量覆盖
4. **渐进增强**：核心功能优先，扩展功能按需添加
5. **自反思机制**：Master 具备答案质量评估和主动补充能力


---

# 附录

启动测试：

```
# 运行所有测试
uv run pytest

# 运行数据库测试
uv run pytest tests/database/ -v

# 运行单个测试文件
uv run pytest tests/database/test_repository.py -v
```
