"""
本文件用户：AI Agent 开发者

结构与功能概述：
- 定义了 sql_worker 类，通过 LangChain 1.x 工具与 SQL 数据库进行交互，支持查询、结构信息获取与 SQL 检查。
- 使用 langchain_community 提供的 SQL 工具构建工具链，并封装为 Agent，可通过自然语言查询数据库。
- 支持通过环境变量自定义 agent 的系统提示词。
- execute 方法可执行用户输入的自然语言数据库查询，并日志记录查询及响应。

使用方式：
1. 在项目根目录的 .env 文件中配置 OPENAI_API_KEY 和 OPENAI_BASE_URL
2. 创建 sql_worker 实例，传入数据库连接字符串
3. 调用 execute 方法，输入自然语言查询，即可获得数据库返回结果
"""

import os
from dotenv import load_dotenv
from loguru import logger
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain.chat_models import init_chat_model


# 加载环境变量
load_dotenv()

system_prompt = """

你是一个 sqlite 数据库管理员，你需要在接到请求以后，自主思考或者调用工具以完成你的工作

在接到请求以后，你的一般工作步骤如下：

1. 调用工具检查数据库有哪些表，判断你负责的数据库是否有可能完成要求，如果不可能完成，那就返回“我做不到”；
2. 如果你认为有可能完成任务，则思考如何构建合适的 sql 语句完成任务要求，假设你构建的 sql 语句为变量 sql_query；
3. 检查并对比你的 sql_query 是否正确、是否和需求相符合；
4. 调用合适的工具，在 sql 表中执行你的 sql_query，得到查询结果；
5. 整理你的工作成果并返回给用户。

"""


class sql_worker:
    """
    构建一个和数据库进行交互的 sql worker agent
    
    从 .env 文件读取配置：
    - OPENAI_API_KEY: OpenAI API 密钥
    - OPENAI_BASE_URL: API 基础 URL（可选，默认 https://api.openai.com/v1）
    - SQL_SYSTEM_PROMPT: 自定义系统提示词（可选）
    """
    def __init__(self, db_url: str):
        self.model = init_chat_model(
            model = "gpt-4o-mini",
            base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            api_key = os.getenv("OPENAI_API_KEY")
        )
        
        # 从环境变量获取配置
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY 未设置，请在 .env 文件中配置")
        
        # 链接数据库并创建 tools
        self.db = SQLDatabase.from_uri(db_url)
        toolkit = SQLDatabaseToolkit(db=self.db, llm=self.model)
        self.tools = toolkit.get_tools()

        # 创建 Agent
        self.agent = create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt=system_prompt,
        )
        
        logger.info(f"SQL Worker 初始化完成，使用模型: gpt-4o-mini, base_url: {base_url}")
    
    def execute(self, query: str):
        resp = self.agent.invoke(
            input = {
                "messages": [
                    HumanMessage(content=query)
                ]
            })
        
        logger.info(f"SQL Query: {query}")
        logger.info(f"SQL Response: {resp}")
        return resp

