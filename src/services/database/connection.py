"""
Database Connection - SQLite 连接管理

负责数据库连接的创建、管理和复用：

1. 连接管理
   - 创建和初始化数据库连接
   - 单例模式确保连接复用
   - 连接状态监控

2. 事务管理
   - 自动事务提交
   - 手动事务控制
   - 事务回滚支持

3. 查询执行
   - 执行原始 SQL
   - 参数化查询防止 SQL 注入
   - 结果集处理

4. 资源管理
   - 连接自动关闭
   - 上下文管理器支持
   - 异常处理
"""

import sqlite3
from typing import Optional, List, Any, Dict
from pathlib import Path
from contextlib import contextmanager

from src.utils.helpers.logger import get_logger

logger = get_logger("database.connection")


class DatabaseConnection:
    """
    SQLite 数据库连接管理器
    
    采用单例模式，确保整个应用共享同一个数据库连接。
    支持上下文管理器和手动连接管理两种使用方式。
    
    使用示例:
        # 方式 1: 获取单例实例
        db = DatabaseConnection("data/scholar.db")
        db.connect()
        results = db.fetchall("SELECT * FROM papers")
        db.close()
        
        # 方式 2: 使用上下文管理器（推荐）
        with DatabaseConnection("data/scholar.db") as db:
            results = db.fetchall("SELECT * FROM papers")
    """
    
    # 单例实例存储
    _instance: Optional["DatabaseConnection"] = None
    _initialized: bool = False
    
    def __new__(cls, db_path: str = None):
        """
        单例模式实现
        
        确保只创建一个 DatabaseConnection 实例。
        如果已存在实例，直接返回；否则创建新实例。
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, db_path: str = None):
        """
        初始化数据库连接管理器
        
        Args:
            db_path: SQLite 数据库文件路径
                     如果文件不存在，会自动创建
        """
        # 避免单例重复初始化
        if DatabaseConnection._initialized and self._connection is not None:
            return
        
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None
        DatabaseConnection._initialized = True
    
    # ============================================================
    # 连接管理
    # ============================================================
    
    def connect(self) -> sqlite3.Connection:
        """
        建立数据库连接
        
        创建 SQLite 连接，并配置以下特性：
        - 启用外键约束
        - 返回字典形式的查询结果（通过 Row 工厂）
        
        Returns:
            sqlite3.Connection 实例
            
        Raises:
            sqlite3.Error: 连接失败时抛出
        """
        if self._connection is not None:
            return self._connection
        
        if not self.db_path:
            raise ValueError("数据库路径未指定")
        
        # 确保父目录存在
        db_file = Path(self.db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"连接数据库: {self.db_path}")
        
        self._connection = sqlite3.connect(
            self.db_path,
            check_same_thread=False  # 允许多线程访问
        )
        
        # 启用外键约束（SQLite 默认不启用）
        self._connection.execute("PRAGMA foreign_keys = ON")
        
        # 设置 Row 工厂，使查询结果可以通过列名访问
        self._connection.row_factory = sqlite3.Row
        
        logger.debug("数据库连接建立成功")
        return self._connection
    
    def close(self) -> None:
        """
        关闭数据库连接
        
        安全关闭连接，释放资源。
        如果连接已关闭或不存在，则静默返回。
        """
        if self._connection is not None:
            logger.info("关闭数据库连接")
            self._connection.close()
            self._connection = None
    
    @property
    def is_connected(self) -> bool:
        """
        检查连接状态
        
        Returns:
            True 表示连接有效，False 表示未连接
        """
        if self._connection is None:
            return False
        
        # 尝试执行简单查询来验证连接有效性
        try:
            self._connection.execute("SELECT 1")
            return True
        except sqlite3.Error:
            return False
    
    # ============================================================
    # 上下文管理器支持
    # ============================================================
    
    def __enter__(self) -> "DatabaseConnection":
        """进入上下文时自动建立连接"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """
        退出上下文时处理事务和关闭连接
        
        - 如果有异常，回滚事务
        - 如果正常退出，提交事务
        - 最后关闭连接
        """
        if exc_type is not None:
            # 发生异常，回滚
            logger.warning(f"检测到异常，回滚事务: {exc_val}")
            self.rollback()
        else:
            # 正常退出，提交
            self.commit()
        
        self.close()
        return False  # 不抑制异常
    
    # ============================================================
    # 游标管理
    # ============================================================
    
    @contextmanager
    def get_cursor(self):
        """
        获取数据库游标（上下文管理器）
        
        提供一个安全的游标获取方式，自动处理游标的关闭。
        
        Yields:
            sqlite3.Cursor 实例
            
        Example:
            with db.get_cursor() as cursor:
                cursor.execute("SELECT * FROM papers")
                rows = cursor.fetchall()
        """
        if self._connection is None:
            self.connect()
        
        cursor = self._connection.cursor()
        try:
            yield cursor
        finally:
            cursor.close()
    
    # ============================================================
    # SQL 执行方法
    # ============================================================
    
    def execute(self, sql: str, params: tuple = None) -> sqlite3.Cursor:
        """
        执行单条 SQL 语句
        
        支持参数化查询，防止 SQL 注入攻击。
        
        Args:
            sql: SQL 语句，使用 ? 作为参数占位符
            params: 参数元组，与占位符一一对应
            
        Returns:
            执行后的 Cursor 对象
            
        Example:
            # 插入数据
            db.execute(
                "INSERT INTO papers (title, authors) VALUES (?, ?)",
                ("Deep Learning", "Goodfellow et al.")
            )
            
            # 查询数据
            cursor = db.execute("SELECT * FROM papers WHERE id = ?", (1,))
        """
        if self._connection is None:
            self.connect()
        
        cursor = self._connection.cursor()
        
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        
        return cursor
    
    def executemany(self, sql: str, params_list: List[tuple]) -> sqlite3.Cursor:
        """
        批量执行 SQL 语句
        
        对多组参数执行相同的 SQL，比循环单条执行更高效。
        
        Args:
            sql: SQL 语句模板
            params_list: 参数元组列表
            
        Returns:
            执行后的 Cursor 对象
            
        Example:
            papers = [
                ("Paper A", "Author A"),
                ("Paper B", "Author B"),
                ("Paper C", "Author C"),
            ]
            db.executemany(
                "INSERT INTO papers (title, authors) VALUES (?, ?)",
                papers
            )
        """
        if self._connection is None:
            self.connect()
        
        cursor = self._connection.cursor()
        cursor.executemany(sql, params_list)
        return cursor
    
    def executescript(self, sql_script: str) -> None:
        """
        执行 SQL 脚本
        
        用于执行包含多条 SQL 语句的脚本，如建表脚本。
        注意：executescript 会先执行 COMMIT，再执行脚本。
        
        Args:
            sql_script: 包含多条 SQL 语句的脚本
            
        Example:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS papers (...);
                CREATE TABLE IF NOT EXISTS notes (...);
                CREATE INDEX IF NOT EXISTS idx_papers_title ON papers(title);
            ''')
        """
        if self._connection is None:
            self.connect()
        
        logger.debug("执行 SQL 脚本")
        self._connection.executescript(sql_script)
    
    # ============================================================
    # 查询快捷方法
    # ============================================================
    
    def fetchall(self, sql: str, params: tuple = None) -> List[sqlite3.Row]:
        """
        查询并返回所有结果
        
        Args:
            sql: SELECT 查询语句
            params: 查询参数
            
        Returns:
            sqlite3.Row 对象列表，每个 Row 可通过列名或索引访问
            
        Example:
            rows = db.fetchall("SELECT title, authors FROM papers")
            for row in rows:
                print(row["title"], row["authors"])
        """
        cursor = self.execute(sql, params)
        return cursor.fetchall()
    
    def fetchone(self, sql: str, params: tuple = None) -> Optional[sqlite3.Row]:
        """
        查询并返回单条结果
        
        Args:
            sql: SELECT 查询语句
            params: 查询参数
            
        Returns:
            单个 sqlite3.Row 对象，如果没有结果则返回 None
            
        Example:
            paper = db.fetchone("SELECT * FROM papers WHERE id = ?", (1,))
            if paper:
                print(paper["title"])
        """
        cursor = self.execute(sql, params)
        return cursor.fetchone()
    
    def fetchval(self, sql: str, params: tuple = None) -> Any:
        """
        查询并返回单个值
        
        适用于 COUNT、MAX 等聚合查询。
        
        Args:
            sql: SELECT 查询语句
            params: 查询参数
            
        Returns:
            查询结果的第一列第一行值，无结果返回 None
            
        Example:
            count = db.fetchval("SELECT COUNT(*) FROM papers")
            max_id = db.fetchval("SELECT MAX(id) FROM papers")
        """
        row = self.fetchone(sql, params)
        return row[0] if row else None
    
    # ============================================================
    # 事务管理
    # ============================================================
    
    def commit(self) -> None:
        """
        提交事务
        
        将当前事务中的所有更改持久化到数据库。
        """
        if self._connection is not None:
            logger.debug("提交事务")
            self._connection.commit()
    
    def rollback(self) -> None:
        """
        回滚事务
        
        撤销当前事务中的所有更改。
        """
        if self._connection is not None:
            logger.debug("回滚事务")
            self._connection.rollback()
    
    # ============================================================
    # 工具方法
    # ============================================================
    
    def table_exists(self, table_name: str) -> bool:
        """
        检查表是否存在
        
        Args:
            table_name: 表名
            
        Returns:
            True 表示表存在，False 表示不存在
        """
        sql = """
            SELECT COUNT(*) FROM sqlite_master 
            WHERE type='table' AND name=?
        """
        count = self.fetchval(sql, (table_name,))
        return count > 0
    
    def get_table_names(self) -> List[str]:
        """
        获取所有表名
        
        Returns:
            数据库中所有用户表的名称列表
        """
        sql = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """
        rows = self.fetchall(sql)
        return [row["name"] for row in rows]
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        获取表结构信息
        
        Args:
            table_name: 表名
            
        Returns:
            列信息列表，每项包含 cid, name, type, notnull, dflt_value, pk
        """
        sql = f"PRAGMA table_info({table_name})"
        rows = self.fetchall(sql)
        return [dict(row) for row in rows]
    
    @classmethod
    def reset_instance(cls) -> None:
        """
        重置单例实例
        
        主要用于测试场景，清除单例状态以便重新初始化。
        """
        if cls._instance is not None:
            cls._instance.close()
        cls._instance = None
        cls._initialized = False
