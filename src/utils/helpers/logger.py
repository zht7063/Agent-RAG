"""
Logger - 日志工具

基于 loguru 提供统一的日志管理功能：

1. 日志配置
   - 日志级别控制（DEBUG, INFO, WARNING, ERROR）
   - 输出目标配置（控制台、文件）
   - 日志格式定制

2. 日志格式
   - 时间戳
   - 日志级别
   - 模块名称
   - 消息内容

3. 日志输出
   - 控制台彩色输出
   - 文件轮转存储
"""

import sys
from pathlib import Path
from typing import Optional
from functools import wraps
from loguru import logger as _logger


# ============================================================
# 默认配置
# ============================================================

DEFAULT_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)

# 简化格式（用于控制台）
SIMPLE_FORMAT = (
    "<green>{time:HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<level>{message}</level>"
)

# 标记是否已初始化
_initialized = False


# ============================================================
# 日志配置函数
# ============================================================

def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    rotation: str = "10 MB",
    retention: str = "7 days"
) -> None:
    """
    配置日志系统
    
    初始化 loguru 日志配置，支持控制台和文件输出。
    如果已经初始化过，则不会重复配置。
    
    Args:
        level: 日志级别（DEBUG, INFO, WARNING, ERROR）
        log_file: 日志文件路径，为 None 则只输出到控制台
        rotation: 日志轮转大小（如 "10 MB", "1 day"）
        retention: 日志保留时间（如 "7 days", "1 week"）
    """
    global _initialized
    
    if _initialized:
        return
    
    # 移除默认 handler，重新配置
    _logger.remove()
    
    # 添加控制台输出
    _logger.add(
        sys.stderr,
        format=SIMPLE_FORMAT,
        level=level,
        colorize=True
    )
    
    # 添加文件输出（如果指定了路径）
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        _logger.add(
            str(log_file),
            format=DEFAULT_FORMAT,
            level=level,
            rotation=rotation,
            retention=retention,
            encoding="utf-8"
        )
    
    _initialized = True
    _logger.debug(f"日志系统初始化完成，级别: {level}")


def get_logger(name: str = None):
    """
    获取 logger 实例
    
    返回带有模块名称绑定的 logger，便于追踪日志来源。
    
    Args:
        name: 模块名称，如 "database.connection"
        
    Returns:
        绑定了模块名称的 logger 实例
    """
    if name:
        return _logger.bind(name=name)
    return _logger


def log_function_call(func):
    """
    函数调用日志装饰器
    
    自动记录函数的调用参数和返回值/异常。
    适用于需要追踪调用链的关键函数。
    
    Example:
        @log_function_call
        def process_data(data):
            return data.upper()
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        _logger.debug(f"调用 {func_name}，参数: args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            _logger.debug(f"{func_name} 返回: {result}")
            return result
        except Exception as e:
            _logger.error(f"{func_name} 异常: {e}")
            raise
    
    return wrapper


# ============================================================
# 日志上下文管理器
# ============================================================

class LogContext:
    """
    日志上下文管理器
    
    用于在特定代码块中添加额外的日志上下文信息。
    上下文信息会自动附加到该块内的所有日志中。
    
    Example:
        with LogContext(user_id=123, action="import"):
            logger.info("开始处理")  # 日志会包含 user_id 和 action
    """
    
    def __init__(self, **context):
        """
        Args:
            **context: 要添加的上下文键值对
        """
        self.context = context
        self._token = None
    
    def __enter__(self):
        self._token = _logger.contextualize(**self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._token:
            self._token.__exit__(exc_type, exc_val, exc_tb)
        return False
