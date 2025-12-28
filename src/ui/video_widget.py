"""
视频显示组件
"""

from typing import Optional, Tuple

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QImage, QPixmap

import cv2
import numpy as np

from src.utils import VideoCapture, VideoSource


class VideoWidget(QWidget):
    """视频显示组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._capture: Optional[VideoCapture] = None
        self._current_frame: Optional[np.ndarray] = None
        self._is_dark_theme = True
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 视频显示标签
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_label.setMinimumSize(640, 480)
        
        # 默认显示文字
        self.video_label.setText("点击开始按钮启动视频")
        self._apply_theme()
        
        layout.addWidget(self.video_label)
    
    def _apply_theme(self):
        """应用主题"""
        if self._is_dark_theme:
            self.video_label.setStyleSheet("""
                QLabel {
                    background-color: #1a1a2e;
                    border: 2px solid #16213e;
                    border-radius: 8px;
                    color: #a0a0a0;
                    font-size: 16px;
                }
            """)
        else:
            self.video_label.setStyleSheet("""
                QLabel {
                    background-color: #e8e8e8;
                    border: 2px solid #cccccc;
                    border-radius: 8px;
                    color: #666666;
                    font-size: 16px;
                }
            """)
    
    def set_dark_theme(self, is_dark: bool):
        """设置主题"""
        self._is_dark_theme = is_dark
        self._apply_theme()
    
    def start_capture(self, source: VideoSource) -> bool:
        """
        开始捕获
        
        Args:
            source: 视频源配置
            
        Returns:
            是否成功
        """
        self.stop_capture()
        
        self._capture = VideoCapture(source)
        if not self._capture.open():
            self._capture = None
            return False
        
        return True
    
    def stop_capture(self):
        """停止捕获"""
        if self._capture is not None:
            self._capture.close()
            self._capture = None
        
        self._current_frame = None
        self.video_label.clear()
        self.video_label.setText("点击开始按钮启动视频")
    
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        读取帧
        
        Returns:
            (是否成功, 图像帧)
        """
        if self._capture is None:
            return False, None
        
        ret, frame = self._capture.read()
        if ret and frame is not None:
            self._current_frame = frame.copy()
        
        return ret, frame
    
    def display_frame(self, frame: np.ndarray):
        """
        显示帧
        
        Args:
            frame: BGR格式图像
        """
        if frame is None:
            return
        
        self._current_frame = frame.copy()
        
        # 转换为RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 获取标签大小
        label_size = self.video_label.size()
        
        # 计算缩放比例（保持宽高比）
        frame_h, frame_w = rgb_frame.shape[:2]
        scale_w = label_size.width() / frame_w
        scale_h = label_size.height() / frame_h
        scale = min(scale_w, scale_h)
        
        new_w = int(frame_w * scale)
        new_h = int(frame_h * scale)
        
        # 缩放
        if scale != 1.0:
            rgb_frame = cv2.resize(rgb_frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        # 转换为QImage
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        q_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        # 显示
        self.video_label.setPixmap(QPixmap.fromImage(q_image))
    
    def get_current_frame(self) -> Optional[np.ndarray]:
        """获取当前帧"""
        return self._current_frame
    
    @property
    def is_video_file(self) -> bool:
        """是否是视频文件"""
        if self._capture is not None:
            return self._capture.is_video_file
        return False
    
    @property
    def frame_delay(self) -> int:
        """帧延迟"""
        if self._capture is not None:
            return self._capture.frame_delay
        return 33
