"""
项目配置抽象类
提供统一的配置接口
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class ColorConfig:
    """颜色配置 (BGR格式)"""
    green: Tuple[int, int, int] = (0, 255, 0)      # 匹配 - 绿色
    red: Tuple[int, int, int] = (0, 0, 255)        # 不匹配 - 红色
    yellow: Tuple[int, int, int] = (0, 255, 255)   # 参考骨架 - 黄色
    white: Tuple[int, int, int] = (255, 255, 255)  # 白色


@dataclass
class DetectorConfig:
    """检测器配置"""
    min_detection_confidence: float = 0.5
    min_tracking_confidence: float = 0.5
    model_path: str = "pose_landmarker.task"


@dataclass
class AnalyzerConfig:
    """分析器配置"""
    angle_threshold: float = 15.0  # 角度差阈值（度数）


@dataclass
class RenderConfig:
    """渲染配置"""
    line_thickness_normal: int = 2
    line_thickness_bold: int = 4
    overlay_alpha: float = 0.4  # 半透明度
    overlay_scale: float = 0.3  # 参考图缩放比例


@dataclass
class WindowConfig:
    """窗口配置"""
    window_name: str = "Pose Comparison System"
    camera_width: int = 1280
    camera_height: int = 720


class BaseConfig(ABC):
    """
    配置抽象基类
    
    所有配置类都需要继承此类并实现抽象方法
    """
    
    @property
    @abstractmethod
    def detector(self) -> DetectorConfig:
        """检测器配置"""
        pass
    
    @property
    @abstractmethod
    def analyzer(self) -> AnalyzerConfig:
        """分析器配置"""
        pass
    
    @property
    @abstractmethod
    def render(self) -> RenderConfig:
        """渲染配置"""
        pass
    
    @property
    @abstractmethod
    def window(self) -> WindowConfig:
        """窗口配置"""
        pass
    
    @property
    @abstractmethod
    def colors(self) -> ColorConfig:
        """颜色配置"""
        pass
    
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键名 (支持点号分隔，如 'detector.min_detection_confidence')
            default: 默认值
            
        Returns:
            配置值
        """
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            key: 配置键名
            value: 配置值
        """
        pass
    
    @abstractmethod
    def load_from_file(self, file_path: str) -> bool:
        """
        从文件加载配置
        
        Args:
            file_path: 配置文件路径
            
        Returns:
            是否加载成功
        """
        pass
    
    @abstractmethod
    def save_to_file(self, file_path: str) -> bool:
        """
        保存配置到文件
        
        Args:
            file_path: 配置文件路径
            
        Returns:
            是否保存成功
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            配置字典
        """
        pass
    
    @abstractmethod
    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        从字典加载配置
        
        Args:
            data: 配置字典
        """
        pass
