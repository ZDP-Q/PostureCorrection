"""
组件注册表
用于注册和管理可用的实现类
"""

from typing import Dict, Type, Any, Optional, Callable
from dataclasses import dataclass, field
import importlib
import inspect
import os
import pkgutil
from pathlib import Path


@dataclass
class ComponentInfo:
    """组件信息"""
    name: str
    cls: Type
    description: str = ""
    category: str = ""  # detector, analyzer, config
    is_default: bool = False


class Registry:
    """
    组件注册表
    
    支持自动发现和注册组件，以及懒加载
    """
    
    _instance: Optional['Registry'] = None
    
    def __new__(cls) -> 'Registry':
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._components: Dict[str, Dict[str, ComponentInfo]] = {
            'detector': {},
            'analyzer': {},
            'config': {},
        }
        self._lazy_imports: Dict[str, Callable] = {}
        self._initialized = True
    
    def register(
        self, 
        category: str, 
        name: str, 
        cls: Type,
        description: str = "",
        is_default: bool = False
    ) -> None:
        """
        注册组件
        
        Args:
            category: 组件类别 (detector, analyzer, config)
            name: 组件名称
            cls: 组件类
            description: 组件描述
            is_default: 是否为默认实现
        """
        if category not in self._components:
            self._components[category] = {}
        
        self._components[category][name] = ComponentInfo(
            name=name,
            cls=cls,
            description=description,
            category=category,
            is_default=is_default
        )
    
    def register_lazy(
        self, 
        category: str, 
        name: str, 
        import_path: str,
        class_name: str,
        description: str = "",
        is_default: bool = False
    ) -> None:
        """
        注册懒加载组件
        
        Args:
            category: 组件类别
            name: 组件名称
            import_path: 模块导入路径
            class_name: 类名
            description: 组件描述
            is_default: 是否为默认实现
        """
        def lazy_loader():
            module = importlib.import_module(import_path)
            return getattr(module, class_name)
        
        self._lazy_imports[f"{category}.{name}"] = lazy_loader
        
        if category not in self._components:
            self._components[category] = {}
        
        # 创建占位符，实际类在首次访问时加载
        self._components[category][name] = ComponentInfo(
            name=name,
            cls=None,  # 懒加载，暂时为None
            description=description,
            category=category,
            is_default=is_default
        )
    
    def get(self, category: str, name: str) -> Optional[Type]:
        """
        获取组件类
        
        Args:
            category: 组件类别
            name: 组件名称
            
        Returns:
            组件类或None
        """
        key = f"{category}.{name}"
        
        # 检查是否需要懒加载
        if key in self._lazy_imports:
            component_info = self._components.get(category, {}).get(name)
            if component_info and component_info.cls is None:
                # 执行懒加载
                component_info.cls = self._lazy_imports[key]()
        
        component_info = self._components.get(category, {}).get(name)
        return component_info.cls if component_info else None
    
    def get_default(self, category: str) -> Optional[Type]:
        """
        获取默认组件类
        
        Args:
            category: 组件类别
            
        Returns:
            默认组件类或None
        """
        components = self._components.get(category, {})
        for info in components.values():
            if info.is_default:
                return self.get(category, info.name)
        
        # 如果没有设置默认，返回第一个
        if components:
            first_name = list(components.keys())[0]
            return self.get(category, first_name)
        
        return None
    
    def get_default_info(self, category: str) -> Optional[ComponentInfo]:
        """
        获取默认组件信息
        
        Args:
            category: 组件类别
            
        Returns:
            默认组件信息或None
        """
        components = self._components.get(category, {})
        for info in components.values():
            if info.is_default:
                return info
        
        # 如果没有设置默认，返回第一个
        if components:
            first_name = list(components.keys())[0]
            return components[first_name]
        
        return None
    
    def list_components(self, category: str) -> Dict[str, ComponentInfo]:
        """
        列出指定类别的所有组件
        
        Args:
            category: 组件类别
            
        Returns:
            组件信息字典
        """
        return self._components.get(category, {}).copy()
    
    def list_all(self) -> Dict[str, Dict[str, ComponentInfo]]:
        """
        列出所有组件
        
        Returns:
            所有组件信息
        """
        return self._components.copy()
    
    def auto_discover(self, package_path: str) -> None:
        """
        自动发现并注册包中的组件
        
        会扫描指定包路径下的所有模块，查找继承自基类的实现类
        
        Args:
            package_path: 包路径
        """
        from src.core import BaseDetector, BaseAnalyzer, BaseConfig
        
        base_classes = {
            'detector': BaseDetector,
            'analyzer': BaseAnalyzer,
            'config': BaseConfig,
        }
        
        # 获取包的目录
        package = importlib.import_module(package_path)
        package_dir = Path(package.__file__).parent
        
        # 遍历包中的所有模块
        for module_info in pkgutil.iter_modules([str(package_dir)]):
            if module_info.name.startswith('_'):
                continue
            
            try:
                module_path = f"{package_path}.{module_info.name}"
                module = importlib.import_module(module_path)
                
                # 查找模块中的类
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    
                    if not inspect.isclass(attr):
                        continue
                    
                    # 检查是否继承自基类
                    for category, base_class in base_classes.items():
                        if (issubclass(attr, base_class) and 
                            attr is not base_class and
                            not inspect.isabstract(attr)):
                            
                            # 获取组件信息 - 尝试实例化以获取 name 和 description
                            try:
                                temp_instance = attr.__new__(attr)
                                # 如果有 name 属性且是 property，则使用类名
                                if hasattr(attr, 'name') and isinstance(getattr(type(temp_instance), 'name', None), property):
                                    # 尝试调用 __init__ 来初始化最小化
                                    temp_instance._model_path = None
                                    temp_instance._min_detection_confidence = 0.5
                                    temp_instance._min_tracking_confidence = 0.5
                                    temp_instance._use_gpu = True
                                    temp_instance._detector = None
                                    temp_instance._analyzer = None
                                    name = temp_instance.name
                                    description = temp_instance.description
                                else:
                                    name = attr.__name__
                                    description = attr.__doc__ or ''
                            except Exception:
                                name = attr.__name__
                                description = attr.__doc__ or ''
                            
                            is_default = getattr(attr, 'is_default', False)
                            
                            self.register(
                                category=category,
                                name=name,
                                cls=attr,
                                description=description,
                                is_default=is_default
                            )
                            break
                            
            except Exception as e:
                print(f"警告: 加载模块 {module_info.name} 时出错: {e}")
    
    def clear(self) -> None:
        """清空注册表"""
        for category in self._components:
            self._components[category].clear()
        self._lazy_imports.clear()


# 全局注册表实例
registry = Registry()
