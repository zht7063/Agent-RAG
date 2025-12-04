"""
Schema Manager - 数据库 Schema 定义和管理

负责数据库表结构的定义、创建和维护：

1. 表结构定义
   - papers: 论文元数据表
   - collections: 文献合集表
   - collection_papers: 合集-论文关联表
   - notes: 研究笔记表
   - experiments: 实验记录表
   - inspirations: 研究灵感表

2. Schema 管理
   - 表创建和初始化
   - 索引创建
   - Schema 版本管理

3. 数据迁移
   - Schema 变更追踪
   - 向前兼容迁移
"""

from typing import Optional, List, Dict, Any

from src.utils.helpers.logger import get_logger

logger = get_logger("database.schema")


# ============================================================
# Schema 定义
# ============================================================

# 数据库版本号，用于追踪 Schema 变更
CURRENT_SCHEMA_VERSION = 1

# SQL 建表语句
SCHEMA_SQL = '''
-- ============================================================
-- 论文元数据表
-- 存储论文的基本信息和本地关联
-- ============================================================
CREATE TABLE IF NOT EXISTS papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,                    -- 论文标题
    authors TEXT,                           -- 作者列表（逗号分隔）
    abstract TEXT,                          -- 摘要
    keywords TEXT,                          -- 关键词（逗号分隔）
    publish_date TEXT,                      -- 发表日期 (YYYY-MM-DD)
    venue TEXT,                             -- 期刊/会议名称
    doi TEXT,                               -- DOI 标识符
    url TEXT,                               -- 论文 URL
    pdf_path TEXT,                          -- 本地 PDF 文件路径
    vector_ids TEXT,                        -- 关联的向量索引 ID（JSON 数组）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 文献合集表
-- 用户自定义的论文分组
-- ============================================================
CREATE TABLE IF NOT EXISTS collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                     -- 合集名称
    description TEXT,                       -- 合集描述
    tags TEXT,                              -- 标签（逗号分隔）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 合集-论文关联表
-- 多对多关系表，一个合集可包含多篇论文，一篇论文可属于多个合集
-- ============================================================
CREATE TABLE IF NOT EXISTS collection_papers (
    collection_id INTEGER,
    paper_id INTEGER,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (collection_id, paper_id),
    FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE,
    FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE
);

-- ============================================================
-- 研究笔记表
-- 与论文关联的阅读笔记和批注
-- ============================================================
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id INTEGER,                       -- 关联的论文 ID（可为空，表示独立笔记）
    content TEXT NOT NULL,                  -- 笔记内容
    note_type TEXT,                         -- 笔记类型: highlight, comment, question
    page_number INTEGER,                    -- 对应的 PDF 页码
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE SET NULL
);

-- ============================================================
-- 实验记录表
-- 研究实验的设计、参数和结果记录
-- ============================================================
CREATE TABLE IF NOT EXISTS experiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                     -- 实验名称
    description TEXT,                       -- 实验描述
    parameters TEXT,                        -- 实验参数（JSON 格式）
    results TEXT,                           -- 实验结果（JSON 格式）
    related_papers TEXT,                    -- 关联论文 ID 列表（JSON 数组）
    status TEXT DEFAULT 'planned',          -- 状态: planned, running, completed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 研究灵感表
-- 跨论文的关联发现和研究方向建议
-- ============================================================
CREATE TABLE IF NOT EXISTS inspirations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,                    -- 灵感标题
    content TEXT,                           -- 灵感内容/详细描述
    source_papers TEXT,                     -- 灵感来源论文 ID（JSON 数组）
    priority TEXT DEFAULT 'medium',         -- 优先级: high, medium, low
    status TEXT DEFAULT 'new',              -- 状态: new, exploring, archived
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Schema 版本表
-- 用于追踪数据库 Schema 版本，支持迁移
-- ============================================================
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- ============================================================
-- 索引定义
-- 为常用查询字段创建索引，提升查询性能
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_papers_title ON papers(title);
CREATE INDEX IF NOT EXISTS idx_papers_keywords ON papers(keywords);
CREATE INDEX IF NOT EXISTS idx_papers_publish_date ON papers(publish_date);
CREATE INDEX IF NOT EXISTS idx_notes_paper_id ON notes(paper_id);
CREATE INDEX IF NOT EXISTS idx_notes_type ON notes(note_type);
CREATE INDEX IF NOT EXISTS idx_experiments_status ON experiments(status);
CREATE INDEX IF NOT EXISTS idx_inspirations_priority ON inspirations(priority);
CREATE INDEX IF NOT EXISTS idx_inspirations_status ON inspirations(status);
'''


# ============================================================
# Schema Manager 类
# ============================================================

class SchemaManager:
    """
    数据库 Schema 管理器
    
    负责数据库表结构的初始化、验证和迁移。
    
    使用示例:
        db = DatabaseConnection("data/scholar.db")
        db.connect()
        
        schema_manager = SchemaManager(db)
        schema_manager.initialize_schema()  # 创建所有表
        
        # 检查表是否存在
        if schema_manager.table_exists("papers"):
            print("papers 表已创建")
    """
    
    # 核心表列表（用于验证 Schema 完整性）
    CORE_TABLES = [
        "papers",
        "collections",
        "collection_papers",
        "notes",
        "experiments",
        "inspirations",
        "schema_version"
    ]
    
    def __init__(self, db_connection):
        """
        初始化 Schema 管理器
        
        Args:
            db_connection: DatabaseConnection 实例
        """
        self.db = db_connection
    
    # ============================================================
    # Schema 初始化
    # ============================================================
    
    def initialize_schema(self) -> None:
        """
        初始化数据库 Schema
        
        执行建表脚本，创建所有必要的表和索引。
        使用 IF NOT EXISTS，可安全重复调用。
        """
        logger.info("初始化数据库 Schema")
        
        # 执行建表脚本
        self.db.executescript(SCHEMA_SQL)
        
        # 记录 Schema 版本
        self._record_schema_version(CURRENT_SCHEMA_VERSION, "初始化 Schema")
        
        self.db.commit()
        logger.info("Schema 初始化完成")
    
    def _record_schema_version(self, version: int, description: str) -> None:
        """
        记录 Schema 版本
        
        Args:
            version: 版本号
            description: 版本描述
        """
        # 检查版本是否已存在
        existing = self.db.fetchval(
            "SELECT version FROM schema_version WHERE version = ?",
            (version,)
        )
        
        if existing is None:
            self.db.execute(
                "INSERT INTO schema_version (version, description) VALUES (?, ?)",
                (version, description)
            )
            logger.debug(f"记录 Schema 版本: v{version} - {description}")
    
    # ============================================================
    # Schema 查询
    # ============================================================
    
    def get_schema_version(self) -> Optional[int]:
        """
        获取当前 Schema 版本
        
        Returns:
            当前版本号，如果 schema_version 表不存在则返回 None
        """
        if not self.table_exists("schema_version"):
            return None
        
        version = self.db.fetchval(
            "SELECT MAX(version) FROM schema_version"
        )
        return version
    
    def get_all_tables(self) -> List[str]:
        """
        获取所有用户表名
        
        Returns:
            表名列表（不含 sqlite 内部表）
        """
        return self.db.get_table_names()
    
    def table_exists(self, table_name: str) -> bool:
        """
        检查指定表是否存在
        
        Args:
            table_name: 表名
            
        Returns:
            True 表示存在，False 表示不存在
        """
        return self.db.table_exists(table_name)
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        获取表结构信息
        
        Args:
            table_name: 表名
            
        Returns:
            列信息列表，每项包含:
            - cid: 列 ID
            - name: 列名
            - type: 数据类型
            - notnull: 是否非空
            - dflt_value: 默认值
            - pk: 是否主键
        """
        return self.db.get_table_info(table_name)
    
    # ============================================================
    # Schema 验证
    # ============================================================
    
    def verify_schema(self) -> Dict[str, Any]:
        """
        验证 Schema 完整性
        
        检查所有核心表是否存在。
        
        Returns:
            验证结果字典:
            - is_valid: 是否完整
            - missing_tables: 缺失的表列表
            - existing_tables: 已存在的表列表
        """
        existing_tables = self.get_all_tables()
        missing_tables = [
            table for table in self.CORE_TABLES 
            if table not in existing_tables
        ]
        
        result = {
            "is_valid": len(missing_tables) == 0,
            "missing_tables": missing_tables,
            "existing_tables": existing_tables,
            "schema_version": self.get_schema_version()
        }
        
        if result["is_valid"]:
            logger.debug("Schema 验证通过")
        else:
            logger.warning(f"Schema 不完整，缺失表: {missing_tables}")
        
        return result
    
    # ============================================================
    # Schema 管理
    # ============================================================
    
    def drop_table(self, table_name: str) -> None:
        """
        删除表（谨慎使用）
        
        Args:
            table_name: 要删除的表名
            
        警告：此操作不可逆，会丢失表中所有数据！
        """
        logger.warning(f"删除表: {table_name}")
        self.db.execute(f"DROP TABLE IF EXISTS {table_name}")
        self.db.commit()
    
    def drop_all_tables(self) -> None:
        """
        删除所有用户表（谨慎使用）
        
        警告：此操作不可逆，会丢失所有数据！
        主要用于测试场景的数据库重置。
        """
        logger.warning("删除所有表")
        
        # 先获取表列表的快照
        tables = list(self.get_all_tables())
        
        # 禁用外键约束以避免删除顺序问题
        self.db.execute("PRAGMA foreign_keys = OFF")
        
        # 删除所有表
        for table in tables:
            self.db.execute(f"DROP TABLE IF EXISTS {table}")
        
        # 重新启用外键约束
        self.db.execute("PRAGMA foreign_keys = ON")
        
        self.db.commit()
        logger.info(f"已删除 {len(tables)} 个表")
    
    # ============================================================
    # Schema 迁移（预留）
    # ============================================================
    
    def migrate(self, target_version: int) -> None:
        """
        执行 Schema 迁移
        
        将 Schema 从当前版本迁移到目标版本。
        
        Args:
            target_version: 目标版本号
            
        Note:
            当前版本仅支持初始化，迁移功能预留给后续版本。
        """
        current = self.get_schema_version()
        
        if current is None:
            # 数据库未初始化，执行完整初始化
            logger.info("数据库未初始化，执行完整 Schema 初始化")
            self.initialize_schema()
            return
        
        if current >= target_version:
            logger.debug(f"当前版本 v{current} >= 目标版本 v{target_version}，无需迁移")
            return
        
        # TODO: 实现增量迁移逻辑
        # 当 Schema 需要变更时，在此添加迁移脚本
        logger.info(f"从 v{current} 迁移到 v{target_version}")
        
        # 示例迁移结构（预留）:
        # migrations = {
        #     2: self._migrate_v1_to_v2,
        #     3: self._migrate_v2_to_v3,
        # }
        # for version in range(current + 1, target_version + 1):
        #     if version in migrations:
        #         migrations[version]()
        #         self._record_schema_version(version, f"迁移到 v{version}")
        
        self.db.commit()
