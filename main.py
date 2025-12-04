import asyncio
import shutil
from pathlib import Path
from src.services.mcp.MCPFetch import test_mcp_fetch


def clean_pycache(root_dir: str | Path = ".") -> int:
    """清理项目中的所有 __pycache__ 缓存文件
    
    Args:
        root_dir: 要清理的根目录路径，默认为当前目录
        
    Returns:
        删除的 __pycache__ 目录数量
    """
    root_path = Path(root_dir).resolve()
    removed_count = 0
    
    for pycache_dir in root_path.rglob("__pycache__"):
        if pycache_dir.is_dir():
            shutil.rmtree(pycache_dir)
            removed_count += 1
            print(f"已删除: {pycache_dir}")
    
    return removed_count



if __name__ == "__main__":
    asyncio.run(test_mcp_fetch())
