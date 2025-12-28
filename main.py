"""
姿态对比系统 - Pose Comparison System
入口文件 (向后兼容的入口)

推荐使用新入口: python -m src.main
"""

import sys


def main():
    """主函数 - 重定向到新入口"""
    from src.main import main as new_main
    new_main()


if __name__ == "__main__":
    main()

