"""
ScholarRAG - 科研文献智能助手

应用入口文件，提供：

1. CLI 交互模式
   - 命令行对话界面
   - 支持多轮对话
   - 命令解析（/help, /clear, /quit）

2. 初始化流程
   - 配置加载和验证
   - 数据库初始化
   - Agent 系统启动

3. 主要功能入口
   - 文献问答
   - 文档添加
   - 数据库查询

使用方式:
    python main.py              # 启动 CLI 交互模式
    python main.py --init       # 初始化数据库
    python main.py --add <path> # 添加文档
"""

import argparse
from pathlib import Path

from config.settings import ensure_directories, SQLITE_DB_PATH, LOG_FILE, LOG_LEVEL
from src.services.database import DatabaseConnection, SchemaManager
from src.utils.helpers import setup_logging, get_logger


# ============================================================
# 数据库初始化
# ============================================================

def init_database():
    """
    初始化数据库
    
    创建数据库文件和所有必要的表结构。
    如果数据库已存在，会验证 Schema 完整性。
    """
    logger = get_logger("main")
    logger.info("开始初始化数据库")
    
    # 创建数据库连接
    db = DatabaseConnection(str(SQLITE_DB_PATH))
    db.connect()
    
    # 初始化 Schema
    schema_manager = SchemaManager(db)
    
    # 检查是否需要初始化
    current_version = schema_manager.get_schema_version()
    
    if current_version is None:
        # 首次初始化
        schema_manager.initialize_schema()
        print(f"✓ 数据库初始化完成: {SQLITE_DB_PATH}")
    else:
        # 验证现有 Schema
        result = schema_manager.verify_schema()
        if result["is_valid"]:
            print(f"✓ 数据库已存在，Schema 版本: v{current_version}")
            print(f"  包含 {len(result['existing_tables'])} 个表")
        else:
            print(f"⚠ Schema 不完整，缺失表: {result['missing_tables']}")
            print("  正在修复...")
            schema_manager.initialize_schema()
            print("✓ Schema 修复完成")
    
    # 显示表信息
    tables = schema_manager.get_all_tables()
    print(f"\n数据库表:")
    for table in tables:
        info = schema_manager.get_table_info(table)
        print(f"  - {table} ({len(info)} 列)")
    
    db.close()


# ============================================================
# 文档添加
# ============================================================

def add_document(path: str):
    """
    添加文档到知识库
    
    支持添加 PDF 文件或网页 URL。
    
    Args:
        path: PDF 文件路径或网页 URL
    """
    logger = get_logger("main")
    
    if path.startswith("http://") or path.startswith("https://"):
        # URL 模式
        logger.info(f"添加网页: {path}")
        print(f"⚠ 网页添加功能尚未实现: {path}")
        # TODO: 调用 HTMLVectorStore 添加网页
    else:
        # 文件模式
        file_path = Path(path)
        if not file_path.exists():
            print(f"✗ 文件不存在: {path}")
            return
        
        if file_path.suffix.lower() == ".pdf":
            logger.info(f"添加 PDF: {file_path}")
            print(f"⚠ PDF 添加功能尚未实现: {file_path}")
            # TODO: 调用 PDFVectorStore 添加 PDF
        else:
            print(f"✗ 不支持的文件类型: {file_path.suffix}")


# ============================================================
# CLI 交互
# ============================================================

def cli_chat():
    """
    CLI 交互模式
    
    启动命令行对话界面，支持与 Agent 进行多轮对话。
    """
    logger = get_logger("main")
    logger.info("启动 CLI 交互模式")
    
    print("\n输入问题开始对话，输入 /quit 退出\n")
    
    # TODO: 初始化 MasterAgent
    # master = MasterAgent()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # 处理命令
            if user_input.startswith("/"):
                command = user_input.lower()
                
                if command == "/quit" or command == "/exit":
                    print("再见！")
                    break
                elif command == "/help":
                    print_help()
                elif command == "/clear":
                    print("\n" * 50)  # 简单清屏
                    print("对话历史已清空")
                    # TODO: master.clear_history()
                else:
                    print(f"未知命令: {command}，输入 /help 查看帮助")
                continue
            
            # TODO: 调用 Agent 处理用户输入
            # response = master.process_query(user_input)
            # print(f"\nAssistant: {response}\n")
            
            print(f"\nAssistant: [Agent 尚未实现] 收到问题: {user_input}\n")
            
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            logger.error(f"处理出错: {e}")
            print(f"✗ 处理出错: {e}")


def print_welcome():
    """打印欢迎信息"""
    welcome = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   ScholarRAG - 科研文献智能助手                          ║
    ║                                                          ║
    ║   命令:                                                  ║
    ║     /help  - 显示帮助信息                                ║
    ║     /clear - 清空对话历史                                ║
    ║     /quit  - 退出程序                                    ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(welcome)


def print_help():
    """打印帮助信息"""
    help_text = """
    可用命令:
      /help   - 显示此帮助信息
      /clear  - 清空对话历史
      /quit   - 退出程序
    
    使用说明:
      - 直接输入问题即可开始对话
      - 支持多轮对话，Agent 会记住上下文
      - 可以询问已添加的论文内容
    
    示例问题:
      - "RAG 技术的主要原理是什么？"
      - "总结一下我收藏的关于 Transformer 的论文"
      - "2024 年有哪些关于多模态的重要论文？"
    """
    print(help_text)


# ============================================================
# 主函数
# ============================================================

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="ScholarRAG - 科研文献智能助手")
    parser.add_argument("--init", action="store_true", help="初始化数据库")
    parser.add_argument("--add", type=str, help="添加文档（PDF 路径或 URL）")
    
    args = parser.parse_args()
    
    # 确保目录存在
    ensure_directories()
    
    # 配置日志
    setup_logging(level=LOG_LEVEL, log_file=LOG_FILE)
    
    if args.init:
        init_database()
    elif args.add:
        add_document(args.add)
    else:
        print_welcome()
        cli_chat()


if __name__ == "__main__":
    main()
