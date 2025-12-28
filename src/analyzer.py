"""
姿态分析器 - 计算肢体向量角度
"""

import math
import numpy as np
from typing import Optional, Tuple, List, Dict

from .config import Config
from .constants import ANGLE_JOINTS
from .models import Landmark


class PoseAnalyzer:
    """姿态分析器 - 计算肢体向量角度"""
    
    @staticmethod
    def calculate_angle(p1: Landmark, p2: Landmark, p3: Landmark) -> float:
        """
        计算三点形成的角度（以p2为顶点）
        
        原理：使用向量夹角公式
        向量 v1 = p1 - p2
        向量 v2 = p3 - p2
        角度 = arccos(v1·v2 / |v1||v2|)
        
        Args:
            p1: 第一个点
            p2: 顶点（角度顶点）
            p3: 第三个点
            
        Returns:
            角度值（度数，0-180）
        """
        # 创建向量
        v1 = np.array([p1.x - p2.x, p1.y - p2.y])
        v2 = np.array([p3.x - p2.x, p3.y - p2.y])
        
        # 计算向量模长
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        
        # 避免除零
        if norm_v1 < 1e-6 or norm_v2 < 1e-6:
            return 0.0
        
        # 计算点积
        dot_product = np.dot(v1, v2)
        
        # 计算夹角（弧度）
        cos_angle = np.clip(dot_product / (norm_v1 * norm_v2), -1.0, 1.0)
        angle_rad = np.arccos(cos_angle)
        
        # 转换为度数
        angle_deg = np.degrees(angle_rad)
        
        return angle_deg
    
    @staticmethod
    def calculate_vector_angle_to_horizontal(p1: Landmark, p2: Landmark) -> float:
        """
        计算两点连线与水平方向的夹角
        用于补充分析肢体朝向
        
        Args:
            p1: 起点
            p2: 终点
            
        Returns:
            角度值（度数，-180到180）
        """
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        
        angle_rad = math.atan2(dy, dx)
        angle_deg = np.degrees(angle_rad)
        
        return angle_deg
    
    @classmethod
    def extract_pose_angles(cls, landmarks: List[Landmark]) -> Dict[str, float]:
        """
        从骨骼点提取所有关节角度
        
        这是归一化的关键步骤！
        通过计算角度而非坐标，消除了距离和位置的影响
        
        Args:
            landmarks: 33个骨骼点列表
            
        Returns:
            角度字典 {关节名称: 角度值}
        """
        angles = {}
        
        for joint, point1, point2, name in ANGLE_JOINTS:
            p_joint = landmarks[joint.value]
            p1 = landmarks[point1.value]
            p2 = landmarks[point2.value]
            
            # 检查可见性
            if (p_joint.visibility > 0.5 and 
                p1.visibility > 0.5 and 
                p2.visibility > 0.5):
                angle = cls.calculate_angle(p1, p_joint, p2)
                angles[name] = angle
            else:
                angles[name] = None  # 点不可见
                
        return angles
    
    @staticmethod
    def compare_angles(angle1: Optional[float], angle2: Optional[float], 
                      threshold: float = Config.ANGLE_THRESHOLD) -> Tuple[bool, float]:
        """
        比较两个角度是否匹配
        
        Args:
            angle1: 第一个角度
            angle2: 第二个角度
            threshold: 容差阈值
            
        Returns:
            (是否匹配, 角度差值)
        """
        if angle1 is None or angle2 is None:
            return True, 0.0  # 如果有点不可见，默认匹配
        
        diff = abs(angle1 - angle2)
        is_matched = diff <= threshold
        
        return is_matched, diff
