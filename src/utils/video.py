"""
视频捕获工具类
"""

from typing import Optional, Union, Tuple, Generator
from enum import Enum
from dataclasses import dataclass

import cv2
import numpy as np


class VideoSourceType(Enum):
    """视频源类型"""
    CAMERA = "camera"
    VIDEO_FILE = "video_file"


@dataclass
class VideoSource:
    """视频源配置"""
    source_type: VideoSourceType
    source: Union[int, str]  # 摄像头ID或视频文件路径
    width: int = 1280
    height: int = 720
    fps: int = 30
    
    @classmethod
    def from_camera(cls, camera_id: int = 0, width: int = 1280, height: int = 720) -> 'VideoSource':
        """从摄像头创建视频源"""
        return cls(
            source_type=VideoSourceType.CAMERA,
            source=camera_id,
            width=width,
            height=height
        )
    
    @classmethod
    def from_file(cls, file_path: str) -> 'VideoSource':
        """从文件创建视频源"""
        return cls(
            source_type=VideoSourceType.VIDEO_FILE,
            source=file_path
        )


class VideoCapture:
    """
    视频捕获器
    
    封装OpenCV VideoCapture，提供统一的视频/摄像头接口
    """
    
    def __init__(self, source: VideoSource):
        """
        初始化视频捕获器
        
        Args:
            source: 视频源配置
        """
        self._source = source
        self._cap: Optional[cv2.VideoCapture] = None
        self._is_opened = False
        self._actual_fps = 30.0
        self._actual_width = 0
        self._actual_height = 0
    
    @property
    def is_opened(self) -> bool:
        """是否已打开"""
        return self._is_opened
    
    @property
    def fps(self) -> float:
        """帧率"""
        return self._actual_fps
    
    @property
    def width(self) -> int:
        """宽度"""
        return self._actual_width
    
    @property
    def height(self) -> int:
        """高度"""
        return self._actual_height
    
    @property
    def frame_delay(self) -> int:
        """帧延迟（毫秒）"""
        return int(1000 / self._actual_fps) if self._actual_fps > 0 else 33
    
    @property
    def is_video_file(self) -> bool:
        """是否是视频文件"""
        return self._source.source_type == VideoSourceType.VIDEO_FILE
    
    def open(self) -> bool:
        """打开视频源"""
        try:
            self._cap = cv2.VideoCapture(self._source.source)
            
            if not self._cap.isOpened():
                return False
            
            # 设置摄像头参数
            if self._source.source_type == VideoSourceType.CAMERA:
                self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._source.width)
                self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._source.height)
            
            # 获取实际参数
            self._actual_width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self._actual_height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self._actual_fps = self._cap.get(cv2.CAP_PROP_FPS) or 30.0
            
            self._is_opened = True
            return True
            
        except Exception as e:
            print(f"打开视频源失败: {e}")
            return False
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        读取一帧
        
        Returns:
            (是否成功, 图像帧)
        """
        if self._cap is None:
            return False, None
        
        ret, frame = self._cap.read()
        
        if not ret and self.is_video_file:
            # 视频文件结束，循环播放
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self._cap.read()
        
        return ret, frame
    
    def read_flipped(self, horizontal: bool = True) -> Tuple[bool, Optional[np.ndarray]]:
        """
        读取翻转后的帧（适用于摄像头镜像显示）
        
        Args:
            horizontal: 是否水平翻转
            
        Returns:
            (是否成功, 图像帧)
        """
        ret, frame = self.read()
        if ret and frame is not None and horizontal:
            frame = cv2.flip(frame, 1)
        return ret, frame
    
    def frames(self, flip: bool = False) -> Generator[np.ndarray, None, None]:
        """
        帧生成器
        
        Args:
            flip: 是否翻转
            
        Yields:
            图像帧
        """
        while True:
            if flip:
                ret, frame = self.read_flipped()
            else:
                ret, frame = self.read()
            
            if not ret or frame is None:
                break
            
            yield frame
    
    def seek(self, frame_number: int) -> None:
        """
        跳转到指定帧
        
        Args:
            frame_number: 帧号
        """
        if self._cap is not None and self.is_video_file:
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    
    def get_total_frames(self) -> int:
        """获取总帧数（仅视频文件）"""
        if self._cap is not None and self.is_video_file:
            return int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))
        return 0
    
    def get_current_frame(self) -> int:
        """获取当前帧号"""
        if self._cap is not None:
            return int(self._cap.get(cv2.CAP_PROP_POS_FRAMES))
        return 0
    
    def close(self) -> None:
        """关闭视频源"""
        if self._cap is not None:
            self._cap.release()
            self._cap = None
        self._is_opened = False
    
    def __enter__(self):
        """上下文管理器入口"""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()
        return False
