import asyncio
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient  
from typing import List
from config.settings import OPENAI_BASE_URL, OPENAI_API_KEY
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, AIMessage, SystemMessage


class MCPFetch:
    def __init__(self):
        self.client_mcp_fetch = MultiServerMCPClient(
            {
                "fetch": {
                    "transport": "streamable_http",
                    "url": "https://mcp.api-inference.modelscope.net/ae877438d9ec4a/mcp"
                }
            }
        )

    async def get_mcp_tools(self) -> List[BaseTool]:
        tools = await self.client_mcp_fetch.get_tools()
        return tools


async def test_mcp_fetch():
    """测试 MCPFetch 获取工具列表"""
    mcp_fetch = MCPFetch()
    tools = await mcp_fetch.get_mcp_tools()
    
    print(f"共发现 {len(tools)} 个工具:\n")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    agent = create_agent(
        model = init_chat_model(model="gpt-4o-mini", base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY),
        tools = tools
    )

    result = await agent.ainvoke(
        input = {"messages": [HumanMessage(content="""
            抓取下面 url 的内容并返回给我：

            https://www.runoob.com/docker/docker-tutorial.html
        """)]}
    )
    print(result)