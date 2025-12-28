"""
数据结构定义
"""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Landmark:
    """单个骨骼点数据"""
    x: float
    y: float
    z: float
    visibility: float


@dataclass
class PoseData:
    """姿态数据结构"""
    landmarks: List[Landmark]
    angles: Dict[str, float]  # 关节角度字典
