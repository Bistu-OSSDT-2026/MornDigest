#!/usr/bin/env python3
"""
run.py — MornDigest 项目入口

启动 Streamlit Web 应用。

使用方式:
    streamlit run run.py

或在 Python 脚本中直接导入使用。
"""

import os
import sys
import logging
from pathlib import Path

# 确保项目根目录在 Python 路径中
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("mordigest")


def main():
    """启动 MornDigest 应用"""
    logger.info("=" * 50)
    logger.info("MornDigest — AI晨间智能简报工具")
    logger.info("启动中...")
    logger.info("=" * 50)

    # Streamlit 会通过 streamlit run run.py 自动执行 frontend.app.main()
    # 此处不执行 main()，由 Streamlit 运行时处理
    from frontend.app import main
    main()


if __name__ == "__main__":
    main()
