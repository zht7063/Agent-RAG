from tests.datasource.test_pdf_toolkit import test_pdf_toolkit
from tests.datasource.test_html_toolkit import test_html_toolkit
from tests.agents.test_worker_sql import test_sql_worker

from dotenv import load_dotenv
from loguru import logger
import os

load_dotenv()
logger.info(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")
logger.info(f"OPENAI_BASE_URL: {os.getenv('OPENAI_BASE_URL')}")

if __name__ == "__main__":
    # splits = test_pdf_toolkit()
    # test_html_toolkit(url = "https://arxiv.org/html/2402.08954v1")
    test_sql_worker(query = "数据库中现共有多少条数据？")
