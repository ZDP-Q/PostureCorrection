"""
依赖注入容器
统一管理和调用所有具体实现的类
"""

from typing import Dict, Type, Any, Optional, TypeVar, Generic, Callable
import threading
from functools import wraps

from .registry import Registry, registry


T = TypeVar('T')


class LazyInstance(Generic[T]):
    """
    懒加载实例包装器
    
    首次访问时才会创建实例
    """
    
    def __init__(self, factory: Callable[[], T]):
        self._factory = factory
        self._instance: Optional[T] = None
        self._lock = threading.Lock()
    
    def get(self) -> T:
        """获取实例（懒加载）"""
        if self._instance is None:
            with self._lock:
                if self._instance is None:
                    self._instance = self._factory()
        return self._instance
    
    def reset(self) -> None:
        """重置实例（下次访问时重新创建）"""
        with self._lock:
            self._instance = None
    
    @property
    def is_initialized(self) -> bool:
        """是否已初始化"""
        return self._instance is not None


class Deps:
    """
    依赖注入容器
    
    提供统一的接口来获取和管理所有依赖组件。
    支持：
    - 自动注册当前目录下的具体实现类
    - 懒加载
    - 单例模式
    - 动态切换实现
    """
    
    _instance: Optional['Deps'] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'Deps':
        """单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._registry = registry
        self._instances: Dict[str, LazyInstance] = {}
        self._configs: Dict[str, Any] = {}
        self._current_selections: Dict[str, str] = {
            'detector': None,
            'analyzer': None,
            'config': None,
        }
        self._initialized = True
        
        # 自动发现并注册组件
        self._auto_register()
    
    def _auto_register(self) -> None:
        """自动注册组件"""
        try:
            self._registry.auto_discover('src.deps')
        except Exception as e:
            print(f"警告: 自动注册组件时出错: {e}")
    
    def _get_instance_key(self, category: str, name: str) -> str:
        """获取实例缓存键"""
        return f"{category}.{name}"
    
    def _create_lazy_instance(self, category: str, name: str) -> LazyInstance:
        """创建懒加载实例"""
        def factory():
            cls = self._registry.get(category, name)
            if cls is None:
                raise ValueError(f"未找到组件: {category}.{name}")
            
            # 创建实例
            instance = cls()
            
            # 如果是检测器，初始化它
            if category == 'detector' and hasattr(instance, 'initialize'):
                instance.initialize()
            
            return instance
        
        return LazyInstance(factory)
    
    def get_detector(self, name: str = None):
        """
        获取检测器实例
        
        Args:
            name: 检测器名称，为None时使用当前选择的或默认的
            
        Returns:
            检测器实例
        """
        from src.core import BaseDetector
        
        if name is None:
            name = self._current_selections.get('detector')
        
        if name is None:
            # 使用默认
            cls = self._registry.get_default('detector')
            if cls is None:
                raise ValueError("没有可用的检测器")
            name = cls.__name__
        
        key = self._get_instance_key('detector', name)
        if key not in self._instances:
            self._instances[key] = self._create_lazy_instance('detector', name)
        
        return self._instances[key].get()
    
    def get_analyzer(self, name: str = None):
        """
        获取分析器实例
        
        Args:
            name: 分析器名称，为None时使用当前选择的或默认的
            
        Returns:
            分析器实例
        """
        from src.core import BaseAnalyzer
        
        if name is None:
            name = self._current_selections.get('analyzer')
        
        if name is None:
            cls = self._registry.get_default('analyzer')
            if cls is None:
                raise ValueError("没有可用的分析器")
            name = cls.__name__
        
        key = self._get_instance_key('analyzer', name)
        if key not in self._instances:
            self._instances[key] = self._create_lazy_instance('analyzer', name)
        
        return self._instances[key].get()
    
    def get_config(self, name: str = None):
        """
        获取配置实例
        
        Args:
            name: 配置名称，为None时使用当前选择的或默认的
            
        Returns:
            配置实例
        """
        from src.core import BaseConfig
        
        if name is None:
            name = self._current_selections.get('config')
        
        if name is None:
            cls = self._registry.get_default('config')
            if cls is None:
                raise ValueError("没有可用的配置")
            name = cls.__name__
        
        key = self._get_instance_key('config', name)
        if key not in self._instances:
            self._instances[key] = self._create_lazy_instance('config', name)
        
        return self._instances[key].get()
    
    def select_detector(self, name: str) -> None:
        """
        选择使用的检测器
        
        Args:
            name: 检测器名称
        """
        if self._registry.get('detector', name) is None:
            raise ValueError(f"未找到检测器: {name}")
        self._current_selections['detector'] = name
    
    def select_analyzer(self, name: str) -> None:
        """
        选择使用的分析器
        
        Args:
            name: 分析器名称
        """
        if self._registry.get('analyzer', name) is None:
            raise ValueError(f"未找到分析器: {name}")
        self._current_selections['analyzer'] = name
    
    def select_config(self, name: str) -> None:
        """
        选择使用的配置
        
        Args:
            name: 配置名称
        """
        if self._registry.get('config', name) is None:
            raise ValueError(f"未找到配置: {name}")
        self._current_selections['config'] = name
    
    def list_detectors(self) -> Dict[str, str]:
        """
        列出所有可用的检测器
        
        Returns:
            {名称: 描述} 字典
        """
        components = self._registry.list_components('detector')
        return {name: info.description for name, info in components.items()}
    
    def list_analyzers(self) -> Dict[str, str]:
        """
        列出所有可用的分析器
        
        Returns:
            {名称: 描述} 字典
        """
        components = self._registry.list_components('analyzer')
        return {name: info.description for name, info in components.items()}
    
    def list_configs(self) -> Dict[str, str]:
        """
        列出所有可用的配置
        
        Returns:
            {名称: 描述} 字典
        """
        components = self._registry.list_components('config')
        return {name: info.description for name, info in components.items()}
    
    def register_detector(
        self, 
        name: str, 
        cls: Type,
        description: str = "",
        is_default: bool = False
    ) -> None:
        """手动注册检测器"""
        self._registry.register('detector', name, cls, description, is_default)
    
    def register_analyzer(
        self, 
        name: str, 
        cls: Type,
        description: str = "",
        is_default: bool = False
    ) -> None:
        """手动注册分析器"""
        self._registry.register('analyzer', name, cls, description, is_default)
    
    def register_config(
        self, 
        name: str, 
        cls: Type,
        description: str = "",
        is_default: bool = False
    ) -> None:
        """手动注册配置"""
        self._registry.register('config', name, cls, description, is_default)
    
    def reset_instance(self, category: str, name: str) -> None:
        """
        重置指定实例（下次访问时重新创建）
        
        Args:
            category: 组件类别
            name: 组件名称
        """
        key = self._get_instance_key(category, name)
        if key in self._instances:
            self._instances[key].reset()
    
    def reset_all(self) -> None:
        """重置所有实例"""
        for lazy_instance in self._instances.values():
            lazy_instance.reset()
    
    def cleanup(self) -> None:
        """清理所有资源"""
        for key, lazy_instance in self._instances.items():
            if lazy_instance.is_initialized:
                instance = lazy_instance.get()
                if hasattr(instance, 'close'):
                    try:
                        instance.close()
                    except Exception as e:
                        print(f"清理 {key} 时出错: {e}")
        
        self._instances.clear()
    
    @classmethod
    def get_instance(cls) -> 'Deps':
        """获取全局依赖注入容器实例"""
        return cls()


# 全局依赖注入容器实例
deps = Deps()


# 便捷函数
def get_detector(name: str = None):
    """获取检测器实例"""
    return deps.get_detector(name)


def get_analyzer(name: str = None):
    """获取分析器实例"""
    return deps.get_analyzer(name)


def get_config(name: str = None):
    """获取配置实例"""
    return deps.get_config(name)
