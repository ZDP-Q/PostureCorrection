"""
依赖注入模块
"""

from .deps import Deps, deps, get_detector, get_analyzer, get_config
from .registry import Registry, registry
from .mediapipe_detector import MediaPipeDetector
from .mediapipe_full_detector import MediaPipeFullDetector
from .mediapipe_heavy_detector import MediaPipeHeavyDetector

__all__ = [
    'Deps',
    'deps',
    'get_detector',
    'get_analyzer',
    'get_config',
    'Registry',
    'registry',
    'MediaPipeDetector',
    'MediaPipeFullDetector',
    'MediaPipeHeavyDetector',
]
