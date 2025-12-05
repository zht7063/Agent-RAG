from tests.datasource.test_pdf_toolkit import test_pdf_toolkit
from tests.datasource.test_html_toolkit import test_html_toolkit
from tests.agents.test_worker_sql import test_sql_worker

if __name__ == "__main__":
    # splits = test_pdf_toolkit()
    # test_html_toolkit(url = "https://arxiv.org/html/2402.08954v1")
    test_sql_worker(query = "告诉我你有哪些工具可以使用？可以做到哪些事情？你可以为现有的表添加、修改或者删除数据吗？")
