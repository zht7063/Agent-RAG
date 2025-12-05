"""
测试 sql_worker 类
"""

from src.agents.worker_sql import sql_worker

def test_sql_worker(query: str):
    # 创建 sql_worker 实例
    worker = sql_worker(db_url="sqlite:///data/scholar.db")
    resp = worker.execute(query)

    print(resp)
    print("-" * 100)
    print(resp["messages"][-1].content)