"""
将 sqlite 数据库中的数据转换为向量数据库
"""
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from config.settings import OPENAI_BASE_URL, OPENAI_API_KEY
from langchain.chat_models import init_chat_model
from pathlib import Path
from loguru import logger
from langchain_community.utilities import SQLDatabase


class SQLiteToolkit:
    def __init__(self, db_path: Path, model: str = "gpt-4o-mini"):
        model = init_chat_model(
            model=model,
            base_url=OPENAI_BASE_URL,
            api_key=OPENAI_API_KEY
        )
        self.db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=model)
    
    def get_tools(self):
        return self.toolkit.get_tools()


def test_sqlite_toolkit():
    db_path = Path("assets/db/Chinook.db")
    toolkit = SQLiteToolkit(db_path)

    for tool in toolkit.get_tools():
        print(tool.name)
        print("-" * 100)
        print(tool.description)
        print("-" * 100)
        print(tool.args)
