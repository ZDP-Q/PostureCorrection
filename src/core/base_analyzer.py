"""
姿势差别计算功能抽象类
提供统一的姿势分析和比较接口
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, List, Dict

from src.models import Landmark, PoseData


class BaseAnalyzer(ABC):
    """
    姿势分析器抽象基类
    
    所有姿势分析器都需要继承此类并实现抽象方法，
    以确保姿势差别计算接口的统一性。
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        分析器名称
        
        Returns:
            分析器的唯一标识名称
        """
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """
        分析器描述
        
        Returns:
            分析器的描述信息
        """
        pass
    
    @abstractmethod
    def calculate_angle(self, p1: Landmark, p2: Landmark, p3: Landmark) -> float:
        """
        计算三点形成的角度（以p2为顶点）
        
        Args:
            p1: 第一个点
            p2: 顶点（角度顶点）
            p3: 第三个点
            
        Returns:
            角度值（度数，0-180）
        """
        pass
    
    @abstractmethod
    def extract_pose_angles(self, landmarks: List[Landmark]) -> Dict[str, float]:
        """
        从骨骼点提取所有关节角度
        
        Args:
            landmarks: 骨骼点列表
            
        Returns:
            角度字典 {关节名称: 角度值}
        """
        pass
    
    @abstractmethod
    def compare_angles(
        self, 
        angle1: Optional[float], 
        angle2: Optional[float], 
        threshold: float = 15.0
    ) -> Tuple[bool, float]:
        """
        比较两个角度是否匹配
        
        Args:
            angle1: 第一个角度
            angle2: 第二个角度
            threshold: 容差阈值
            
        Returns:
            (是否匹配, 角度差值)
        """
        pass
    
    @abstractmethod
    def compare_poses(
        self, 
        pose1: PoseData, 
        pose2: PoseData,
        threshold: float = 15.0
    ) -> Tuple[Dict[str, bool], float]:
        """
        比较两个姿态的差异
        
        Args:
            pose1: 第一个姿态 (通常是标准姿态)
            pose2: 第二个姿态 (通常是用户姿态)
            threshold: 角度差阈值
            
        Returns:
            (各肢体段匹配结果字典, 总体匹配率)
        """
        pass
    
    @abstractmethod
    def get_pose_difference_details(
        self, 
        pose1: PoseData, 
        pose2: PoseData
    ) -> Dict[str, Dict[str, float]]:
        """
        获取两个姿态的详细差异信息
        
        Args:
            pose1: 第一个姿态
            pose2: 第二个姿态
            
        Returns:
            详细差异字典 {关节名: {'angle1': float, 'angle2': float, 'diff': float}}
        """
        pass
    
    @abstractmethod
    def calculate_similarity_score(self, pose1: PoseData, pose2: PoseData) -> float:
        """
        计算两个姿态的相似度得分
        
        Args:
            pose1: 第一个姿态
            pose2: 第二个姿态
            
        Returns:
            相似度得分 (0.0 - 1.0)
        """
        pass
