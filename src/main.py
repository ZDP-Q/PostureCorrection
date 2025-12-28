"""
姿态对比系统 - 主入口
支持三种运行模式: dev, release, test
支持命令行和UI界面启动
"""

import argparse
import sys
from enum import Enum
from typing import Optional


class RunMode(Enum):
    """运行模式"""
    DEV = "dev"
    RELEASE = "release"
    TEST = "test"


def setup_logging(mode: RunMode):
    """根据模式设置日志"""
    import logging
    
    if mode == RunMode.DEV:
        level = logging.DEBUG
    elif mode == RunMode.TEST:
        level = logging.INFO
    else:
        level = logging.WARNING
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def run_cli(args):
    """运行命令行模式"""
    from src.app import PoseComparisonApp
    
    # 确定输入源
    if args.video:
        input_source = args.video
    else:
        input_source = args.camera
    
    # 创建并运行应用
    app = PoseComparisonApp()
    
    if args.capture:
        # 捕获参考姿态模式
        from src.utils import create_sample_reference
        create_sample_reference()
    else:
        # 运行姿态对比
        app.run(
            input_source=input_source,
            reference_path=args.reference
        )


def run_gui(args):
    """运行GUI模式"""
    from PyQt5.QtWidgets import QApplication
    from src.ui import MainWindow
    
    app = QApplication(sys.argv)
    
    # 设置应用信息
    app.setApplicationName("Pose Comparison System")
    app.setOrganizationName("PoseApp")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 如果提供了参数，预设配置
    if args.reference:
        window.set_reference_image(args.reference)
    
    sys.exit(app.exec_())


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="姿态对比系统 - Pose Comparison System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
运行模式:
  dev     - 开发模式，显示详细日志
  release - 发布模式，仅显示警告和错误
  test    - 测试模式，用于自动化测试

示例:
  python -m src.main --mode dev --gui              # 开发模式启动UI
  python -m src.main --mode release -r pose.jpg   # 发布模式命令行
  python -m src.main --capture                     # 捕获参考姿态
        """
    )
    
    # 运行模式
    parser.add_argument(
        "--mode", "-m",
        type=str,
        choices=["dev", "release", "test"],
        default="release",
        help="运行模式 (default: release)"
    )
    
    # UI模式
    parser.add_argument(
        "--gui", "-g",
        action="store_true",
        help="启动图形界面"
    )
    
    # 参考图像
    parser.add_argument(
        "--reference", "-r",
        type=str,
        default=None,
        help="参考图像路径"
    )
    
    # 摄像头
    parser.add_argument(
        "--camera", "-c",
        type=int,
        default=0,
        help="摄像头ID (default: 0)"
    )
    
    # 视频文件
    parser.add_argument(
        "--video", "-v",
        type=str,
        default=None,
        help="使用视频文件代替摄像头"
    )
    
    # 捕获模式
    parser.add_argument(
        "--capture",
        action="store_true",
        help="捕获参考姿态模式"
    )
    
    # 解析参数
    args = parser.parse_args()
    
    # 设置运行模式
    mode = RunMode(args.mode)
    setup_logging(mode)
    
    # 运行
    if args.gui:
        run_gui(args)
    else:
        run_cli(args)


if __name__ == "__main__":
    main()
