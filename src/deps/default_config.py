"""
默认配置实现
"""

import json
from typing import Any, Dict
from dataclasses import dataclass, field, asdict
from pathlib import Path

from src.core import BaseConfig
from src.core.base_config import (
    ColorConfig, DetectorConfig, AnalyzerConfig, 
    RenderConfig, WindowConfig
)


class DefaultConfig(BaseConfig):
    """
    默认配置实现
    
    提供系统的默认配置参数
    """
    
    is_default = True
    
    def __init__(self):
        self._detector = DetectorConfig()
        self._analyzer = AnalyzerConfig()
        self._render = RenderConfig()
        self._window = WindowConfig()
        self._colors = ColorConfig()
        self._custom: Dict[str, Any] = {}
    
    @property
    def name(self) -> str:
        return "DefaultConfig"
    
    @property
    def description(self) -> str:
        return "默认配置 - 提供系统的默认配置参数"
    
    @property
    def detector(self) -> DetectorConfig:
        return self._detector
    
    @property
    def analyzer(self) -> AnalyzerConfig:
        return self._analyzer
    
    @property
    def render(self) -> RenderConfig:
        return self._render
    
    @property
    def window(self) -> WindowConfig:
        return self._window
    
    @property
    def colors(self) -> ColorConfig:
        return self._colors
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        parts = key.split('.')
        
        if len(parts) == 1:
            # 顶级配置
            if hasattr(self, f'_{key}'):
                return getattr(self, f'_{key}')
            return self._custom.get(key, default)
        
        # 嵌套配置
        section = parts[0]
        attr = parts[1]
        
        section_obj = getattr(self, f'_{section}', None)
        if section_obj is not None and hasattr(section_obj, attr):
            return getattr(section_obj, attr)
        
        return default
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        parts = key.split('.')
        
        if len(parts) == 1:
            self._custom[key] = value
            return
        
        section = parts[0]
        attr = parts[1]
        
        section_obj = getattr(self, f'_{section}', None)
        if section_obj is not None and hasattr(section_obj, attr):
            setattr(section_obj, attr, value)
    
    def load_from_file(self, file_path: str) -> bool:
        """从文件加载配置"""
        try:
            path = Path(file_path)
            if not path.exists():
                return False
            
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.from_dict(data)
            return True
            
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return False
    
    def save_to_file(self, file_path: str) -> bool:
        """保存配置到文件"""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'detector': asdict(self._detector),
            'analyzer': asdict(self._analyzer),
            'render': asdict(self._render),
            'window': asdict(self._window),
            'colors': asdict(self._colors),
            'custom': self._custom,
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """从字典加载配置"""
        if 'detector' in data:
            for k, v in data['detector'].items():
                if hasattr(self._detector, k):
                    setattr(self._detector, k, v)
        
        if 'analyzer' in data:
            for k, v in data['analyzer'].items():
                if hasattr(self._analyzer, k):
                    setattr(self._analyzer, k, v)
        
        if 'render' in data:
            for k, v in data['render'].items():
                if hasattr(self._render, k):
                    setattr(self._render, k, v)
        
        if 'window' in data:
            for k, v in data['window'].items():
                if hasattr(self._window, k):
                    setattr(self._window, k, v)
        
        if 'colors' in data:
            for k, v in data['colors'].items():
                if hasattr(self._colors, k):
                    setattr(self._colors, k, tuple(v) if isinstance(v, list) else v)
        
        if 'custom' in data:
            self._custom.update(data['custom'])
