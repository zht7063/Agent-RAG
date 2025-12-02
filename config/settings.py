import os
from dotenv import load_dotenv
from pathlib import Path
import subprocess


load_dotenv()

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def project_root() -> Path:
    """ 获取项目根目录

    命令：`git rev-parse --show-toplevel` 可以快速找到 git 仓库的根目录，

    通过 `subprocess.check_output([...])` 执行 shell 命令，返回字符串结果，

    去掉结果两端的空白字符，得到一个 Path 对象并返回

    """
    git_root = subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"],
        text=True
    ).strip()
    return Path(git_root)

