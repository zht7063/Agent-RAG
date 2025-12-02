基于项目目标和当前状态，建议按以下步骤实现：

## 实现步骤规划

### 阶段一：基础服务层（Foundation Layer）
**目标**：建立基础设施，为上层功能提供支撑

1. **配置管理** (`config/settings.py`)
   - 环境变量读取（API Keys、模型配置）
   - LLM 模型配置（Qwen/OpenAI）
   - 向量数据库配置
   - MCP 服务配置
   - 日志配置

2. **文档处理服务** (`src/services/document/`)
   - PDF 解析和分块（已有 VectorStore，可抽取通用文档处理逻辑）
   - 文档预处理和清洗
   - 元数据提取

3. **数据库服务** (`src/services/database/`)
   - SQLite 连接管理
   - Schema 自动发现和分析
   - 基础查询执行接口

### 阶段二：工具层（Tools Layer）
**目标**：实现 Agent 可调用的工具集

4. **数据库工具集** (`src/utils/tools/database/`)
   - 数据库构建工具（创建、初始化、数据导入）
   - 数据库分析工具（schema 分析、统计查询）
   - 数据库操作工具（NL2SQL、CRUD 操作）
   - 数据验证工具

5. **文档检索工具** (`src/utils/tools/document/`)
   - 向量检索工具（封装 VectorStore）
   - 多页上下文关联检索
   - 答案来源追溯

6. **辅助工具** (`src/utils/helpers/`)
   - 文本处理和清洗
   - 格式化输出
   - 日志工具
   - 错误处理

### 阶段三：外部知识集成（External Knowledge）
**目标**：接入外部知识源

7. **MCP 协议集成** (`src/services/mcp/`)
   - MCP 客户端封装
   - Wiki 知识库查询服务
   - 网页搜索服务
   - 搜索结果质量评估和去重

### 阶段四：Worker Agent（Worker Layer）
**目标**：实现专业化的工作代理

8. **基础 Worker Agent** (`src/agents/worker/base.py`)
   - Worker 基类（工具调用、结果格式化）
   - Worker 注册机制

9. **专业化 Worker**
   - 检索 Worker (`src/agents/worker/retrieval_worker.py`)
     - 文档检索、向量搜索
   - 分析 Worker (`src/agents/worker/analysis_worker.py`)
     - 数据分析、SQL 查询
   - 生成 Worker (`src/agents/worker/generation_worker.py`)
     - 答案生成、文档总结

### 阶段五：Master Agent（Master Layer）
**目标**：实现主控代理，协调多个 Worker

10. **Master Agent** (`src/agents/master/`)
    - 任务复杂度分析
    - 任务分解和子任务生成
    - Worker 调度（并行/串行）
    - 结果汇总和验证
    - 多轮对话上下文管理

### 阶段六：智能问答系统（RAG System）
**目标**：整合为完整的问答系统

11. **RAG 核心逻辑**
    - 意图识别和路由
    - 多源检索整合（向量库 + 数据库 + MCP）
    - 答案生成和置信度评估
    - 多轮对话上下文理解

### 阶段七：应用集成（Application Layer）
**目标**：整合为可运行的应用

12. **主应用入口** (`main.py`)
    - FastAPI 服务（可选）
    - CLI 接口
    - 应用初始化

13. **扩展功能**（可选）
    - 文档生成与总结 (`src/utils/tools/document_generation/`)
    - 批量任务处理
    - 性能优化

## 实现原则

1. 自底向上：先完成服务层和工具层，再构建 Agent 层
2. 独立可测：每个模块可独立测试，降低耦合
3. 迭代开发：每阶段产出可运行的最小功能集
4. 接口优先：定义清晰的接口，便于后续扩展

## 建议的优先级

- 高优先级：阶段一、二、四、五（核心功能）
- 中优先级：阶段三、六（增强功能）
- 低优先级：阶段七扩展功能（可选）

建议从阶段一开始，逐步向上构建。需要我帮你从某个阶段开始实现吗？