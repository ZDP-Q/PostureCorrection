"""
姿态检测器 - MediaPipe 姿态检测封装
"""

import os
import urllib.request
from typing import Optional

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

from .config import Config
from .models import Landmark, PoseData
from .analyzer import PoseAnalyzer


class PoseDetector:
    """MediaPipe 姿态检测封装 - 使用 Tasks API"""
    
    MODEL_URL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
    MODEL_PATH = "pose_landmarker.task"
    
    def __init__(self):
        # 下载模型文件（如果不存在）
        self._ensure_model_downloaded()
        
        # 创建 PoseLandmarker (启用 GPU 加速)
        base_options = mp_python.BaseOptions(
            model_asset_path=self.MODEL_PATH,
            delegate=mp_python.BaseOptions.Delegate.GPU
        )
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            min_pose_detection_confidence=Config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=Config.MIN_TRACKING_CONFIDENCE
        )
        self.detector = vision.PoseLandmarker.create_from_options(options)
        
    def _ensure_model_downloaded(self):
        """确保模型文件已下载"""
        if not os.path.exists(self.MODEL_PATH):
            print("正在下载 MediaPipe 姿态模型...")
            urllib.request.urlretrieve(self.MODEL_URL, self.MODEL_PATH)
            print(f"模型下载完成: {self.MODEL_PATH}")
                
    def detect(self, image: np.ndarray) -> Optional[PoseData]:
        """
        检测图像中的姿态
        
        Args:
            image: BGR格式的图像
            
        Returns:
            PoseData 或 None（未检测到姿态）
        """
        # 转换为RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 创建 MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
        
        # 运行检测
        results = self.detector.detect(mp_image)
        
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
        angles = PoseAnalyzer.extract_pose_angles(landmarks)
        
        return PoseData(landmarks=landmarks, angles=angles)
    
    def detect_from_file(self, image_path: str) -> Optional[PoseData]:
        """从文件检测姿态"""
        image = cv2.imread(image_path)
        if image is None:
            print(f"错误：无法读取图像 {image_path}")
            return None
        return self.detect(image)
    
    def close(self):
        """释放资源"""
        self.detector.close()
