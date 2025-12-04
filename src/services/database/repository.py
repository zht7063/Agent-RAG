"""
Repository - 数据访问层

提供各数据表的 CRUD 操作接口：

1. PaperRepository - 论文元数据管理
   - 论文的增删改查
   - 按关键词、作者、时间检索
   - 批量导入和导出

2. CollectionRepository - 文献合集管理
   - 合集的创建和维护
   - 论文与合集的关联
   - 合集内容检索

3. NoteRepository - 研究笔记管理
   - 笔记的增删改查
   - 按论文检索笔记
   - 笔记类型筛选

4. ExperimentRepository - 实验记录管理
   - 实验的创建和更新
   - 实验状态追踪
   - 关联论文管理

5. InspirationRepository - 研究灵感管理
   - 灵感记录
   - 优先级和状态管理
   - 来源论文关联
"""

from typing import List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from src.utils.helpers.logger import get_logger

logger = get_logger("database.repository")


# ============================================================
# 数据模型定义
# ============================================================

@dataclass
class Paper:
    """
    论文数据模型
    
    Attributes:
        id: 主键 ID（自增）
        title: 论文标题
        authors: 作者列表（逗号分隔）
        abstract: 摘要
        keywords: 关键词（逗号分隔）
        publish_date: 发表日期 (YYYY-MM-DD)
        venue: 期刊/会议名称
        doi: DOI 标识符
        url: 论文 URL
        pdf_path: 本地 PDF 文件路径
        vector_ids: 关联的向量索引 ID（JSON 数组字符串）
        created_at: 创建时间
        updated_at: 更新时间
    """
    id: Optional[int] = None
    title: str = ""
    authors: str = ""
    abstract: str = ""
    keywords: str = ""
    publish_date: str = ""
    venue: str = ""
    doi: str = ""
    url: str = ""
    pdf_path: str = ""
    vector_ids: str = ""
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class Collection:
    """
    文献合集数据模型
    
    Attributes:
        id: 主键 ID
        name: 合集名称
        description: 合集描述
        tags: 标签（逗号分隔）
        created_at: 创建时间
    """
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    tags: str = ""
    created_at: datetime = None


@dataclass
class Note:
    """
    研究笔记数据模型
    
    Attributes:
        id: 主键 ID
        paper_id: 关联的论文 ID（可为空）
        content: 笔记内容
        note_type: 笔记类型 (highlight, comment, question)
        page_number: 对应的 PDF 页码
        created_at: 创建时间
    """
    id: Optional[int] = None
    paper_id: Optional[int] = None
    content: str = ""
    note_type: str = ""
    page_number: Optional[int] = None
    created_at: datetime = None


@dataclass
class Experiment:
    """
    实验记录数据模型
    
    Attributes:
        id: 主键 ID
        name: 实验名称
        description: 实验描述
        parameters: 实验参数（JSON 字符串）
        results: 实验结果（JSON 字符串）
        related_papers: 关联论文 ID（JSON 数组字符串）
        status: 状态 (planned, running, completed)
        created_at: 创建时间
        updated_at: 更新时间
    """
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    parameters: str = ""
    results: str = ""
    related_papers: str = ""
    status: str = "planned"
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class Inspiration:
    """
    研究灵感数据模型
    
    Attributes:
        id: 主键 ID
        title: 灵感标题
        content: 灵感内容/详细描述
        source_papers: 灵感来源论文 ID（JSON 数组字符串）
        priority: 优先级 (high, medium, low)
        status: 状态 (new, exploring, archived)
        created_at: 创建时间
    """
    id: Optional[int] = None
    title: str = ""
    content: str = ""
    source_papers: str = ""
    priority: str = "medium"
    status: str = "new"
    created_at: datetime = None


# ============================================================
# 基础 Repository 类
# ============================================================

class BaseRepository:
    """
    Repository 基类
    
    提供通用的数据库操作辅助方法。
    """
    
    def __init__(self, db_connection):
        """
        初始化 Repository
        
        Args:
            db_connection: DatabaseConnection 实例
        """
        self.db = db_connection
    
    def _row_to_dict(self, row) -> dict:
        """
        将 sqlite3.Row 转换为字典
        
        Args:
            row: sqlite3.Row 对象
            
        Returns:
            字典形式的行数据
        """
        if row is None:
            return None
        return dict(row)


# ============================================================
# PaperRepository - 论文元数据仓储
# ============================================================

class PaperRepository(BaseRepository):
    """
    论文元数据仓储
    
    提供论文数据的完整 CRUD 操作和多种检索方式。
    
    使用示例:
        repo = PaperRepository(db)
        
        # 创建论文
        paper = Paper(title="Attention Is All You Need", authors="Vaswani et al.")
        paper_id = repo.create(paper)
        
        # 检索论文
        paper = repo.get_by_id(paper_id)
        papers = repo.search_by_keywords("transformer")
    """
    
    def create(self, paper: Paper) -> int:
        """
        创建论文记录
        
        Args:
            paper: Paper 数据对象
            
        Returns:
            新创建记录的 ID
        """
        sql = """
            INSERT INTO papers (
                title, authors, abstract, keywords, publish_date,
                venue, doi, url, pdf_path, vector_ids
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            paper.title, paper.authors, paper.abstract, paper.keywords,
            paper.publish_date, paper.venue, paper.doi, paper.url,
            paper.pdf_path, paper.vector_ids
        )
        
        cursor = self.db.execute(sql, params)
        self.db.commit()
        
        paper_id = cursor.lastrowid
        logger.debug(f"创建论文记录: ID={paper_id}, title={paper.title}")
        return paper_id
    
    def get_by_id(self, paper_id: int) -> Optional[Paper]:
        """
        根据 ID 获取论文
        
        Args:
            paper_id: 论文 ID
            
        Returns:
            Paper 对象，如果不存在则返回 None
        """
        sql = "SELECT * FROM papers WHERE id = ?"
        row = self.db.fetchone(sql, (paper_id,))
        
        if row is None:
            return None
        
        return Paper(**self._row_to_dict(row))
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[Paper]:
        """
        获取所有论文（分页）
        
        Args:
            limit: 每页数量，默认 100
            offset: 偏移量，默认 0
            
        Returns:
            Paper 对象列表
        """
        sql = "SELECT * FROM papers ORDER BY created_at DESC LIMIT ? OFFSET ?"
        rows = self.db.fetchall(sql, (limit, offset))
        
        return [Paper(**self._row_to_dict(row)) for row in rows]
    
    def search_by_title(self, title: str) -> List[Paper]:
        """
        按标题模糊搜索
        
        Args:
            title: 搜索关键词
            
        Returns:
            匹配的 Paper 列表
        """
        sql = "SELECT * FROM papers WHERE title LIKE ? ORDER BY created_at DESC"
        rows = self.db.fetchall(sql, (f"%{title}%",))
        
        return [Paper(**self._row_to_dict(row)) for row in rows]
    
    def search_by_keywords(self, keywords: str) -> List[Paper]:
        """
        按关键词模糊搜索
        
        Args:
            keywords: 搜索关键词
            
        Returns:
            匹配的 Paper 列表
        """
        sql = "SELECT * FROM papers WHERE keywords LIKE ? ORDER BY created_at DESC"
        rows = self.db.fetchall(sql, (f"%{keywords}%",))
        
        return [Paper(**self._row_to_dict(row)) for row in rows]
    
    def search_by_author(self, author: str) -> List[Paper]:
        """
        按作者模糊搜索
        
        Args:
            author: 作者名
            
        Returns:
            匹配的 Paper 列表
        """
        sql = "SELECT * FROM papers WHERE authors LIKE ? ORDER BY created_at DESC"
        rows = self.db.fetchall(sql, (f"%{author}%",))
        
        return [Paper(**self._row_to_dict(row)) for row in rows]
    
    def search(self, query: str) -> List[Paper]:
        """
        全文搜索（标题、摘要、关键词、作者）
        
        Args:
            query: 搜索关键词
            
        Returns:
            匹配的 Paper 列表
        """
        sql = """
            SELECT * FROM papers 
            WHERE title LIKE ? OR abstract LIKE ? OR keywords LIKE ? OR authors LIKE ?
            ORDER BY created_at DESC
        """
        pattern = f"%{query}%"
        rows = self.db.fetchall(sql, (pattern, pattern, pattern, pattern))
        
        return [Paper(**self._row_to_dict(row)) for row in rows]
    
    def update(self, paper: Paper) -> bool:
        """
        更新论文记录
        
        Args:
            paper: Paper 数据对象（必须包含 id）
            
        Returns:
            True 表示更新成功
        """
        sql = """
            UPDATE papers SET
                title = ?, authors = ?, abstract = ?, keywords = ?,
                publish_date = ?, venue = ?, doi = ?, url = ?,
                pdf_path = ?, vector_ids = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        params = (
            paper.title, paper.authors, paper.abstract, paper.keywords,
            paper.publish_date, paper.venue, paper.doi, paper.url,
            paper.pdf_path, paper.vector_ids, paper.id
        )
        
        cursor = self.db.execute(sql, params)
        self.db.commit()
        
        success = cursor.rowcount > 0
        if success:
            logger.debug(f"更新论文记录: ID={paper.id}")
        return success
    
    def delete(self, paper_id: int) -> bool:
        """
        删除论文记录
        
        Args:
            paper_id: 论文 ID
            
        Returns:
            True 表示删除成功
        """
        sql = "DELETE FROM papers WHERE id = ?"
        cursor = self.db.execute(sql, (paper_id,))
        self.db.commit()
        
        success = cursor.rowcount > 0
        if success:
            logger.debug(f"删除论文记录: ID={paper_id}")
        return success
    
    def count(self) -> int:
        """
        获取论文总数
        
        Returns:
            论文记录数量
        """
        return self.db.fetchval("SELECT COUNT(*) FROM papers")
    
    def exists(self, paper_id: int) -> bool:
        """
        检查论文是否存在
        
        Args:
            paper_id: 论文 ID
            
        Returns:
            True 表示存在
        """
        count = self.db.fetchval(
            "SELECT COUNT(*) FROM papers WHERE id = ?", 
            (paper_id,)
        )
        return count > 0


# ============================================================
# CollectionRepository - 文献合集仓储
# ============================================================

class CollectionRepository(BaseRepository):
    """
    文献合集仓储
    
    管理文献合集的创建、维护以及与论文的关联关系。
    
    使用示例:
        repo = CollectionRepository(db)
        
        # 创建合集
        collection = Collection(name="Transformer 相关论文")
        coll_id = repo.create(collection)
        
        # 添加论文到合集
        repo.add_paper(coll_id, paper_id)
    """
    
    def create(self, collection: Collection) -> int:
        """
        创建合集
        
        Args:
            collection: Collection 数据对象
            
        Returns:
            新创建记录的 ID
        """
        sql = """
            INSERT INTO collections (name, description, tags)
            VALUES (?, ?, ?)
        """
        params = (collection.name, collection.description, collection.tags)
        
        cursor = self.db.execute(sql, params)
        self.db.commit()
        
        collection_id = cursor.lastrowid
        logger.debug(f"创建合集: ID={collection_id}, name={collection.name}")
        return collection_id
    
    def get_by_id(self, collection_id: int) -> Optional[Collection]:
        """
        根据 ID 获取合集
        
        Args:
            collection_id: 合集 ID
            
        Returns:
            Collection 对象，不存在则返回 None
        """
        sql = "SELECT * FROM collections WHERE id = ?"
        row = self.db.fetchone(sql, (collection_id,))
        
        if row is None:
            return None
        
        return Collection(**self._row_to_dict(row))
    
    def get_all(self) -> List[Collection]:
        """
        获取所有合集
        
        Returns:
            Collection 对象列表
        """
        sql = "SELECT * FROM collections ORDER BY created_at DESC"
        rows = self.db.fetchall(sql)
        
        return [Collection(**self._row_to_dict(row)) for row in rows]
    
    def add_paper(self, collection_id: int, paper_id: int) -> bool:
        """
        添加论文到合集
        
        Args:
            collection_id: 合集 ID
            paper_id: 论文 ID
            
        Returns:
            True 表示添加成功
        """
        sql = """
            INSERT OR IGNORE INTO collection_papers (collection_id, paper_id)
            VALUES (?, ?)
        """
        cursor = self.db.execute(sql, (collection_id, paper_id))
        self.db.commit()
        
        success = cursor.rowcount > 0
        if success:
            logger.debug(f"添加论文到合集: collection={collection_id}, paper={paper_id}")
        return success
    
    def remove_paper(self, collection_id: int, paper_id: int) -> bool:
        """
        从合集移除论文
        
        Args:
            collection_id: 合集 ID
            paper_id: 论文 ID
            
        Returns:
            True 表示移除成功
        """
        sql = "DELETE FROM collection_papers WHERE collection_id = ? AND paper_id = ?"
        cursor = self.db.execute(sql, (collection_id, paper_id))
        self.db.commit()
        
        success = cursor.rowcount > 0
        if success:
            logger.debug(f"从合集移除论文: collection={collection_id}, paper={paper_id}")
        return success
    
    def get_papers(self, collection_id: int) -> List[Paper]:
        """
        获取合集中的所有论文
        
        Args:
            collection_id: 合集 ID
            
        Returns:
            Paper 对象列表
        """
        sql = """
            SELECT p.* FROM papers p
            INNER JOIN collection_papers cp ON p.id = cp.paper_id
            WHERE cp.collection_id = ?
            ORDER BY cp.added_at DESC
        """
        rows = self.db.fetchall(sql, (collection_id,))
        
        return [Paper(**self._row_to_dict(row)) for row in rows]
    
    def get_paper_count(self, collection_id: int) -> int:
        """
        获取合集中的论文数量
        
        Args:
            collection_id: 合集 ID
            
        Returns:
            论文数量
        """
        sql = "SELECT COUNT(*) FROM collection_papers WHERE collection_id = ?"
        return self.db.fetchval(sql, (collection_id,))
    
    def update(self, collection: Collection) -> bool:
        """
        更新合集
        
        Args:
            collection: Collection 数据对象（必须包含 id）
            
        Returns:
            True 表示更新成功
        """
        sql = """
            UPDATE collections SET
                name = ?, description = ?, tags = ?
            WHERE id = ?
        """
        params = (
            collection.name, collection.description, 
            collection.tags, collection.id
        )
        
        cursor = self.db.execute(sql, params)
        self.db.commit()
        
        success = cursor.rowcount > 0
        if success:
            logger.debug(f"更新合集: ID={collection.id}")
        return success
    
    def delete(self, collection_id: int) -> bool:
        """
        删除合集
        
        注意：由于外键 ON DELETE CASCADE，关联关系会自动删除。
        
        Args:
            collection_id: 合集 ID
            
        Returns:
            True 表示删除成功
        """
        sql = "DELETE FROM collections WHERE id = ?"
        cursor = self.db.execute(sql, (collection_id,))
        self.db.commit()
        
        success = cursor.rowcount > 0
        if success:
            logger.debug(f"删除合集: ID={collection_id}")
        return success


# ============================================================
# NoteRepository - 研究笔记仓储
# ============================================================

class NoteRepository(BaseRepository):
    """
    研究笔记仓储
    
    管理与论文关联的阅读笔记和批注。
    
    使用示例:
        repo = NoteRepository(db)
        
        # 创建笔记
        note = Note(paper_id=1, content="重要观点", note_type="highlight")
        note_id = repo.create(note)
        
        # 获取论文的所有笔记
        notes = repo.get_by_paper(paper_id=1)
    """
    
    def create(self, note: Note) -> int:
        """
        创建笔记
        
        Args:
            note: Note 数据对象
            
        Returns:
            新创建记录的 ID
        """
        sql = """
            INSERT INTO notes (paper_id, content, note_type, page_number)
            VALUES (?, ?, ?, ?)
        """
        params = (note.paper_id, note.content, note.note_type, note.page_number)
        
        cursor = self.db.execute(sql, params)
        self.db.commit()
        
        note_id = cursor.lastrowid
        logger.debug(f"创建笔记: ID={note_id}, type={note.note_type}")
        return note_id
    
    def get_by_id(self, note_id: int) -> Optional[Note]:
        """
        根据 ID 获取笔记
        
        Args:
            note_id: 笔记 ID
            
        Returns:
            Note 对象，不存在则返回 None
        """
        sql = "SELECT * FROM notes WHERE id = ?"
        row = self.db.fetchone(sql, (note_id,))
        
        if row is None:
            return None
        
        return Note(**self._row_to_dict(row))
    
    def get_by_paper(self, paper_id: int) -> List[Note]:
        """
        获取论文的所有笔记
        
        Args:
            paper_id: 论文 ID
            
        Returns:
            Note 对象列表
        """
        sql = "SELECT * FROM notes WHERE paper_id = ? ORDER BY created_at DESC"
        rows = self.db.fetchall(sql, (paper_id,))
        
        return [Note(**self._row_to_dict(row)) for row in rows]
    
    def get_by_type(self, note_type: str) -> List[Note]:
        """
        按笔记类型获取
        
        Args:
            note_type: 笔记类型 (highlight, comment, question)
            
        Returns:
            Note 对象列表
        """
        sql = "SELECT * FROM notes WHERE note_type = ? ORDER BY created_at DESC"
        rows = self.db.fetchall(sql, (note_type,))
        
        return [Note(**self._row_to_dict(row)) for row in rows]
    
    def get_all(self, limit: int = 100) -> List[Note]:
        """
        获取所有笔记
        
        Args:
            limit: 返回数量限制
            
        Returns:
            Note 对象列表
        """
        sql = "SELECT * FROM notes ORDER BY created_at DESC LIMIT ?"
        rows = self.db.fetchall(sql, (limit,))
        
        return [Note(**self._row_to_dict(row)) for row in rows]
    
    def update(self, note: Note) -> bool:
        """
        更新笔记
        
        Args:
            note: Note 数据对象（必须包含 id）
            
        Returns:
            True 表示更新成功
        """
        sql = """
            UPDATE notes SET
                paper_id = ?, content = ?, note_type = ?, page_number = ?
            WHERE id = ?
        """
        params = (
            note.paper_id, note.content, note.note_type, 
            note.page_number, note.id
        )
        
        cursor = self.db.execute(sql, params)
        self.db.commit()
        
        success = cursor.rowcount > 0
        if success:
            logger.debug(f"更新笔记: ID={note.id}")
        return success
    
    def delete(self, note_id: int) -> bool:
        """
        删除笔记
        
        Args:
            note_id: 笔记 ID
            
        Returns:
            True 表示删除成功
        """
        sql = "DELETE FROM notes WHERE id = ?"
        cursor = self.db.execute(sql, (note_id,))
        self.db.commit()
        
        success = cursor.rowcount > 0
        if success:
            logger.debug(f"删除笔记: ID={note_id}")
        return success


# ============================================================
# ExperimentRepository - 实验记录仓储
# ============================================================

class ExperimentRepository(BaseRepository):
    """
    实验记录仓储
    
    管理研究实验的设计、参数、结果和状态追踪。
    
    使用示例:
        repo = ExperimentRepository(db)
        
        # 创建实验
        exp = Experiment(name="BERT 微调实验", status="planned")
        exp_id = repo.create(exp)
        
        # 更新状态
        repo.update_status(exp_id, "running")
    """
    
    def create(self, experiment: Experiment) -> int:
        """
        创建实验记录
        
        Args:
            experiment: Experiment 数据对象
            
        Returns:
            新创建记录的 ID
        """
        sql = """
            INSERT INTO experiments (
                name, description, parameters, results, related_papers, status
            ) VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            experiment.name, experiment.description, experiment.parameters,
            experiment.results, experiment.related_papers, experiment.status
        )
        
        cursor = self.db.execute(sql, params)
        self.db.commit()
        
        exp_id = cursor.lastrowid
        logger.debug(f"创建实验记录: ID={exp_id}, name={experiment.name}")
        return exp_id
    
    def get_by_id(self, experiment_id: int) -> Optional[Experiment]:
        """
        根据 ID 获取实验
        
        Args:
            experiment_id: 实验 ID
            
        Returns:
            Experiment 对象，不存在则返回 None
        """
        sql = "SELECT * FROM experiments WHERE id = ?"
        row = self.db.fetchone(sql, (experiment_id,))
        
        if row is None:
            return None
        
        return Experiment(**self._row_to_dict(row))
    
    def get_all(self) -> List[Experiment]:
        """
        获取所有实验
        
        Returns:
            Experiment 对象列表
        """
        sql = "SELECT * FROM experiments ORDER BY created_at DESC"
        rows = self.db.fetchall(sql)
        
        return [Experiment(**self._row_to_dict(row)) for row in rows]
    
    def get_by_status(self, status: str) -> List[Experiment]:
        """
        按状态获取实验
        
        Args:
            status: 实验状态 (planned, running, completed)
            
        Returns:
            Experiment 对象列表
        """
        sql = "SELECT * FROM experiments WHERE status = ? ORDER BY created_at DESC"
        rows = self.db.fetchall(sql, (status,))
        
        return [Experiment(**self._row_to_dict(row)) for row in rows]
    
    def update(self, experiment: Experiment) -> bool:
        """
        更新实验记录
        
        Args:
            experiment: Experiment 数据对象（必须包含 id）
            
        Returns:
            True 表示更新成功
        """
        sql = """
            UPDATE experiments SET
                name = ?, description = ?, parameters = ?, results = ?,
                related_papers = ?, status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        params = (
            experiment.name, experiment.description, experiment.parameters,
            experiment.results, experiment.related_papers, experiment.status,
            experiment.id
        )
        
        cursor = self.db.execute(sql, params)
        self.db.commit()
        
        success = cursor.rowcount > 0
        if success:
            logger.debug(f"更新实验记录: ID={experiment.id}")
        return success
    
    def update_status(self, experiment_id: int, status: str) -> bool:
        """
        更新实验状态
        
        Args:
            experiment_id: 实验 ID
            status: 新状态 (planned, running, completed)
            
        Returns:
            True 表示更新成功
        """
        sql = """
            UPDATE experiments SET 
                status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        cursor = self.db.execute(sql, (status, experiment_id))
        self.db.commit()
        
        success = cursor.rowcount > 0
        if success:
            logger.debug(f"更新实验状态: ID={experiment_id}, status={status}")
        return success
    
    def delete(self, experiment_id: int) -> bool:
        """
        删除实验记录
        
        Args:
            experiment_id: 实验 ID
            
        Returns:
            True 表示删除成功
        """
        sql = "DELETE FROM experiments WHERE id = ?"
        cursor = self.db.execute(sql, (experiment_id,))
        self.db.commit()
        
        success = cursor.rowcount > 0
        if success:
            logger.debug(f"删除实验记录: ID={experiment_id}")
        return success


# ============================================================
# InspirationRepository - 研究灵感仓储
# ============================================================

class InspirationRepository(BaseRepository):
    """
    研究灵感仓储
    
    管理跨论文的关联发现和研究方向建议。
    
    使用示例:
        repo = InspirationRepository(db)
        
        # 记录灵感
        idea = Inspiration(
            title="多模态 RAG 优化方向",
            priority="high",
            status="new"
        )
        idea_id = repo.create(idea)
        
        # 获取高优先级灵感
        ideas = repo.get_by_priority("high")
    """
    
    def create(self, inspiration: Inspiration) -> int:
        """
        创建灵感记录
        
        Args:
            inspiration: Inspiration 数据对象
            
        Returns:
            新创建记录的 ID
        """
        sql = """
            INSERT INTO inspirations (
                title, content, source_papers, priority, status
            ) VALUES (?, ?, ?, ?, ?)
        """
        params = (
            inspiration.title, inspiration.content, inspiration.source_papers,
            inspiration.priority, inspiration.status
        )
        
        cursor = self.db.execute(sql, params)
        self.db.commit()
        
        idea_id = cursor.lastrowid
        logger.debug(f"创建灵感记录: ID={idea_id}, title={inspiration.title}")
        return idea_id
    
    def get_by_id(self, inspiration_id: int) -> Optional[Inspiration]:
        """
        根据 ID 获取灵感
        
        Args:
            inspiration_id: 灵感 ID
            
        Returns:
            Inspiration 对象，不存在则返回 None
        """
        sql = "SELECT * FROM inspirations WHERE id = ?"
        row = self.db.fetchone(sql, (inspiration_id,))
        
        if row is None:
            return None
        
        return Inspiration(**self._row_to_dict(row))
    
    def get_all(self) -> List[Inspiration]:
        """
        获取所有灵感
        
        Returns:
            Inspiration 对象列表
        """
        sql = "SELECT * FROM inspirations ORDER BY created_at DESC"
        rows = self.db.fetchall(sql)
        
        return [Inspiration(**self._row_to_dict(row)) for row in rows]
    
    def get_by_priority(self, priority: str) -> List[Inspiration]:
        """
        按优先级获取
        
        Args:
            priority: 优先级 (high, medium, low)
            
        Returns:
            Inspiration 对象列表
        """
        sql = "SELECT * FROM inspirations WHERE priority = ? ORDER BY created_at DESC"
        rows = self.db.fetchall(sql, (priority,))
        
        return [Inspiration(**self._row_to_dict(row)) for row in rows]
    
    def get_by_status(self, status: str) -> List[Inspiration]:
        """
        按状态获取
        
        Args:
            status: 状态 (new, exploring, archived)
            
        Returns:
            Inspiration 对象列表
        """
        sql = "SELECT * FROM inspirations WHERE status = ? ORDER BY created_at DESC"
        rows = self.db.fetchall(sql, (status,))
        
        return [Inspiration(**self._row_to_dict(row)) for row in rows]
    
    def update(self, inspiration: Inspiration) -> bool:
        """
        更新灵感记录
        
        Args:
            inspiration: Inspiration 数据对象（必须包含 id）
            
        Returns:
            True 表示更新成功
        """
        sql = """
            UPDATE inspirations SET
                title = ?, content = ?, source_papers = ?,
                priority = ?, status = ?
            WHERE id = ?
        """
        params = (
            inspiration.title, inspiration.content, inspiration.source_papers,
            inspiration.priority, inspiration.status, inspiration.id
        )
        
        cursor = self.db.execute(sql, params)
        self.db.commit()
        
        success = cursor.rowcount > 0
        if success:
            logger.debug(f"更新灵感记录: ID={inspiration.id}")
        return success
    
    def update_status(self, inspiration_id: int, status: str) -> bool:
        """
        更新灵感状态
        
        Args:
            inspiration_id: 灵感 ID
            status: 新状态 (new, exploring, archived)
            
        Returns:
            True 表示更新成功
        """
        sql = "UPDATE inspirations SET status = ? WHERE id = ?"
        cursor = self.db.execute(sql, (status, inspiration_id))
        self.db.commit()
        
        success = cursor.rowcount > 0
        if success:
            logger.debug(f"更新灵感状态: ID={inspiration_id}, status={status}")
        return success
    
    def delete(self, inspiration_id: int) -> bool:
        """
        删除灵感记录
        
        Args:
            inspiration_id: 灵感 ID
            
        Returns:
            True 表示删除成功
        """
        sql = "DELETE FROM inspirations WHERE id = ?"
        cursor = self.db.execute(sql, (inspiration_id,))
        self.db.commit()
        
        success = cursor.rowcount > 0
        if success:
            logger.debug(f"删除灵感记录: ID={inspiration_id}")
        return success
