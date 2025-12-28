"""
默认姿势分析器实现
"""

import math
from typing import Optional, Tuple, List, Dict

import numpy as np

from src.core import BaseAnalyzer
from src.models import Landmark, PoseData
from src.constants import ANGLE_JOINTS, LIMB_TO_ANGLES


class DefaultAnalyzer(BaseAnalyzer):
    """
    默认姿势分析器实现
    
    使用向量夹角公式计算关节角度，并进行姿态比较
    """
    
    is_default = True
    
    def __init__(self, angle_threshold: float = 15.0):
        """
        初始化分析器
        
        Args:
            angle_threshold: 默认角度差阈值
        """
        self._angle_threshold = angle_threshold
    
    @property
    def name(self) -> str:
        return "DefaultAnalyzer"
    
    @property
    def description(self) -> str:
        return "默认姿势分析器 - 使用向量夹角公式计算关节角度"
    
    def calculate_angle(self, p1: Landmark, p2: Landmark, p3: Landmark) -> float:
        """
        计算三点形成的角度（以p2为顶点）
        
        原理：使用向量夹角公式
        向量 v1 = p1 - p2
        向量 v2 = p3 - p2
        角度 = arccos(v1·v2 / |v1||v2|)
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
        return np.degrees(angle_rad)
    
    def calculate_vector_angle_to_horizontal(self, p1: Landmark, p2: Landmark) -> float:
        """
        计算两点连线与水平方向的夹角
        用于补充分析肢体朝向
        """
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        
        angle_rad = math.atan2(dy, dx)
        return np.degrees(angle_rad)
    
    def extract_pose_angles(self, landmarks: List[Landmark]) -> Dict[str, float]:
        """
        从骨骼点提取所有关节角度
        
        这是归一化的关键步骤！
        通过计算角度而非坐标，消除了距离和位置的影响
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
                angle = self.calculate_angle(p1, p_joint, p2)
                angles[name] = angle
            else:
                angles[name] = None  # 点不可见
        
        return angles
    
    def compare_angles(
        self, 
        angle1: Optional[float], 
        angle2: Optional[float], 
        threshold: float = None
    ) -> Tuple[bool, float]:
        """比较两个角度是否匹配"""
        if threshold is None:
            threshold = self._angle_threshold
        
        if angle1 is None or angle2 is None:
            return True, 0.0  # 如果有点不可见，默认匹配
        
        diff = abs(angle1 - angle2)
        is_matched = diff <= threshold
        
        return is_matched, diff
    
    def compare_poses(
        self, 
        pose1: PoseData, 
        pose2: PoseData,
        threshold: float = None
    ) -> Tuple[Dict[str, bool], float]:
        """比较两个姿态的差异"""
        if threshold is None:
            threshold = self._angle_threshold
        
        # 比较每个关节角度
        angle_matches = {}
        for name in pose1.angles:
            std_angle = pose1.angles.get(name)
            user_angle = pose2.angles.get(name)
            matched, _ = self.compare_angles(std_angle, user_angle, threshold)
            angle_matches[name] = matched
        
        # 将角度匹配结果映射到肢体段
        limb_matches = {}
        for limb_name, related_angles in LIMB_TO_ANGLES.items():
            if not related_angles:
                limb_matches[limb_name] = True
            else:
                limb_matches[limb_name] = all(
                    angle_matches.get(angle_name, True) 
                    for angle_name in related_angles
                )
        
        # 计算总体匹配率
        valid_angles = [m for name, m in angle_matches.items() 
                       if pose1.angles.get(name) is not None]
        if valid_angles:
            match_ratio = sum(valid_angles) / len(valid_angles)
        else:
            match_ratio = 0.0
        
        return limb_matches, match_ratio
    
    def get_pose_difference_details(
        self, 
        pose1: PoseData, 
        pose2: PoseData
    ) -> Dict[str, Dict[str, float]]:
        """获取两个姿态的详细差异信息"""
        details = {}
        
        for name in pose1.angles:
            angle1 = pose1.angles.get(name)
            angle2 = pose2.angles.get(name)
            
            if angle1 is not None and angle2 is not None:
                details[name] = {
                    'angle1': angle1,
                    'angle2': angle2,
                    'diff': abs(angle1 - angle2)
                }
            else:
                details[name] = {
                    'angle1': angle1,
                    'angle2': angle2,
                    'diff': None
                }
        
        return details
    
    def calculate_similarity_score(self, pose1: PoseData, pose2: PoseData) -> float:
        """
        计算两个姿态的相似度得分
        
        使用基于角度差的相似度计算
        """
        total_weight = 0.0
        weighted_similarity = 0.0
        
        for name in pose1.angles:
            angle1 = pose1.angles.get(name)
            angle2 = pose2.angles.get(name)
            
            if angle1 is not None and angle2 is not None:
                diff = abs(angle1 - angle2)
                # 使用高斯函数计算相似度，diff=0时为1，diff越大越接近0
                similarity = np.exp(-(diff ** 2) / (2 * 30 ** 2))  # sigma=30度
                weighted_similarity += similarity
                total_weight += 1.0
        
        if total_weight > 0:
            return weighted_similarity / total_weight
        return 0.0
