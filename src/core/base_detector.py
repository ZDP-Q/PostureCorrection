"""
关键点识别模型抽象类
提供统一的接口，支持切换不同的关键点识别模型
"""

from abc import ABC, abstractmethod
from typing import Optional, List
import numpy as np

from src.models import PoseData, Landmark


class BaseDetector(ABC):
    """
    关键点识别模型抽象基类
    
    所有关键点识别模型都需要继承此类并实现抽象方法，
    以确保对外接口的统一性。
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        模型名称
        
        Returns:
            模型的唯一标识名称
        """
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """
        模型描述
        
        Returns:
            模型的描述信息
        """
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        初始化模型
        
        Returns:
            是否初始化成功
        """
        pass
    
    @abstractmethod
    def detect(self, image: np.ndarray) -> Optional[PoseData]:
        """
        检测图像中的姿态
        
        Args:
            image: BGR格式的图像 (numpy数组)
            
        Returns:
            PoseData 或 None（未检测到姿态）
        """
        pass
    
    @abstractmethod
    def detect_batch(self, images: List[np.ndarray]) -> List[Optional[PoseData]]:
        """
        批量检测图像中的姿态
        
        Args:
            images: BGR格式的图像列表
            
        Returns:
            PoseData列表，未检测到的位置为None
        """
        pass
    
    def detect_from_file(self, image_path: str) -> Optional[PoseData]:
        """
        从文件检测姿态
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            PoseData 或 None
        """
        import cv2
        image = cv2.imread(image_path)
        if image is None:
            print(f"错误：无法读取图像 {image_path}")
            return None
        return self.detect(image)
    
    @abstractmethod
    def close(self) -> None:
        """释放模型资源"""
        pass
    
    def __enter__(self):
        """上下文管理器入口"""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()
        return False
