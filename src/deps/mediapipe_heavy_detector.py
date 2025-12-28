"""
MediaPipe Heavy 姿态检测器实现
使用重量级模型，精度最高
"""

import os
import urllib.request
from typing import Optional, List

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

from src.core import BaseDetector
from src.models import Landmark, PoseData


class MediaPipeHeavyDetector(BaseDetector):
    """
    MediaPipe Heavy 姿态检测器
    
    使用重量级模型，精度最高，但速度最慢
    适合对精度要求非常高、实时性要求较低的场景
    """
    
    is_default = False
    
    MODEL_URL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task"
    DEFAULT_MODEL_PATH = "models/pose_landmarker_heavy.task"
    
    def __init__(
        self, 
        model_path: str = None,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        use_gpu: bool = True
    ):
        """
        初始化检测器
        
        Args:
            model_path: 模型文件路径
            min_detection_confidence: 最小检测置信度
            min_tracking_confidence: 最小跟踪置信度
            use_gpu: 是否使用GPU加速
        """
        self._model_path = model_path or self.DEFAULT_MODEL_PATH
        self._min_detection_confidence = min_detection_confidence
        self._min_tracking_confidence = min_tracking_confidence
        self._use_gpu = use_gpu
        self._detector = None
        self._analyzer = None
    
    @property
    def name(self) -> str:
        return "MediaPipe-Heavy"
    
    @property
    def description(self) -> str:
        return "MediaPipe Heavy 姿态检测器 - 重量级模型，精度最高"
    
    def _ensure_model_downloaded(self) -> None:
        """确保模型文件已下载"""
        # 确保目录存在
        os.makedirs(os.path.dirname(self._model_path), exist_ok=True)
        
        if not os.path.exists(self._model_path):
            print(f"正在下载 MediaPipe Heavy 姿态模型到 {self._model_path}...")
            urllib.request.urlretrieve(self.MODEL_URL, self._model_path)
            print(f"模型下载完成: {self._model_path}")
    
    def initialize(self) -> bool:
        """初始化模型"""
        try:
            self._ensure_model_downloaded()
            
            # 设置委托（GPU或CPU）
            delegate = (mp_python.BaseOptions.Delegate.GPU 
                       if self._use_gpu 
                       else mp_python.BaseOptions.Delegate.CPU)
            
            base_options = mp_python.BaseOptions(
                model_asset_path=self._model_path,
                delegate=delegate
            )
            
            options = vision.PoseLandmarkerOptions(
                base_options=base_options,
                running_mode=vision.RunningMode.IMAGE,
                min_pose_detection_confidence=self._min_detection_confidence,
                min_tracking_confidence=self._min_tracking_confidence
            )
            
            self._detector = vision.PoseLandmarker.create_from_options(options)
            return True
            
        except Exception as e:
            print(f"初始化检测器失败: {e}")
            # 尝试使用CPU
            if self._use_gpu:
                print("尝试使用CPU模式...")
                self._use_gpu = False
                return self.initialize()
            return False
    
    def _get_analyzer(self):
        """懒加载获取分析器"""
        if self._analyzer is None:
            from src.deps import deps
            self._analyzer = deps.get_analyzer()
        return self._analyzer
    
    def detect(self, image: np.ndarray) -> Optional[PoseData]:
        """检测图像中的姿态"""
        if self._detector is None:
            if not self.initialize():
                return None
        
        # 转换为RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 创建 MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
        
        # 运行检测
        results = self._detector.detect(mp_image)
        
        if not results.pose_landmarks or len(results.pose_landmarks) == 0:
            return None
        
        # 提取骨骼点（取第一个检测到的人）
        pose_landmarks = results.pose_landmarks[0]
        landmarks = []
        for lm in pose_landmarks:
            landmarks.append(Landmark(
                x=lm.x,
                y=lm.y,
                z=lm.z,
                visibility=lm.visibility if hasattr(lm, 'visibility') else 1.0
            ))
        
        # 计算角度
        analyzer = self._get_analyzer()
        angles = analyzer.extract_pose_angles(landmarks)
        
        return PoseData(landmarks=landmarks, angles=angles)
    
    def detect_batch(self, images: List[np.ndarray]) -> List[Optional[PoseData]]:
        """批量检测图像中的姿态"""
        return [self.detect(image) for image in images]
    
    def close(self) -> None:
        """释放资源"""
        if self._detector is not None:
            self._detector.close()
            self._detector = None
