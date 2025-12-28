"""
姿态对比系统 - Pose Comparison System
使用 OpenCV + MediaPipe 实现实时姿态检测与参考姿态对比

重构后的项目结构:
- src/core: 抽象基类
- src/deps: 依赖注入和具体实现
- src/utils: 工具类
- src/ui: Qt5界面
- src/main.py: 入口文件
"""

# 数据模型（保持原有位置以保持兼容性）
from .models import Landmark, PoseData
from .constants import PoseLandmark, SKELETON_CONNECTIONS, ANGLE_JOINTS, LIMB_TO_ANGLES

# 核心抽象类
from .core import BaseDetector, BaseConfig, BaseAnalyzer

# 依赖注入
from .deps import Deps, deps

# 应用
from .app import PoseComparisonApp

# 工具
from .utils import VideoCapture, VideoSource, PoseRenderer, create_sample_reference


__all__ = [
    # 数据模型
    'Landmark',
    'PoseData',
    'PoseLandmark',
    'SKELETON_CONNECTIONS',
    'ANGLE_JOINTS',
    'LIMB_TO_ANGLES',
    
    # 抽象类
    'BaseDetector',
    'BaseConfig',
    'BaseAnalyzer',
    
    # 依赖注入
    'Deps',
    'deps',
    
    # 应用
    'PoseComparisonApp',
    
    # 工具
    'VideoCapture',
    'VideoSource',
    'PoseRenderer',
    'create_sample_reference',
]

__version__ = '2.0.0'
