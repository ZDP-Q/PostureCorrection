"""
文字渲染工具 - 支持中文文字渲染
"""

import os
from typing import Tuple, Optional

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


class ChineseTextRenderer:
    """中文文字渲染器"""
    
    # 常用Windows中文字体路径
    FONT_PATHS = [
        "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
        "C:/Windows/Fonts/simhei.ttf",    # 黑体
        "C:/Windows/Fonts/simsun.ttc",    # 宋体
        "C:/Windows/Fonts/simkai.ttf",    # 楷体
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # Linux 文泉驿正黑
        "/System/Library/Fonts/PingFang.ttc",  # macOS 苹方
    ]
    
    _instance = None
    _font_cache = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._default_font_path = self._find_chinese_font()
    
    def _find_chinese_font(self) -> Optional[str]:
        """查找可用的中文字体"""
        for font_path in self.FONT_PATHS:
            if os.path.exists(font_path):
                return font_path
        return None
    
    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """获取指定大小的字体（带缓存）"""
        if size not in self._font_cache:
            if self._default_font_path:
                self._font_cache[size] = ImageFont.truetype(
                    self._default_font_path, size
                )
            else:
                # 如果没有找到中文字体，使用默认字体
                self._font_cache[size] = ImageFont.load_default()
        return self._font_cache[size]
    
    def put_text(
        self, 
        image: np.ndarray, 
        text: str, 
        position: Tuple[int, int],
        font_size: int = 20,
        color: Tuple[int, int, int] = (255, 255, 255),
        bg_color: Optional[Tuple[int, int, int]] = None
    ) -> np.ndarray:
        """
        在图像上绘制中文文字
        
        Args:
            image: OpenCV图像 (BGR格式)
            text: 要绘制的文字
            position: 文字位置 (x, y)
            font_size: 字体大小
            color: 文字颜色 (BGR格式)
            bg_color: 背景颜色 (BGR格式), None表示透明
            
        Returns:
            绘制后的图像
        """
        if image is None or text is None:
            return image
        
        # 转换为PIL图像 (BGR -> RGB)
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_image)
        
        # 获取字体
        font = self._get_font(font_size)
        
        # 转换颜色 (BGR -> RGB)
        rgb_color = (color[2], color[1], color[0])
        
        # 绘制背景
        if bg_color is not None:
            rgb_bg_color = (bg_color[2], bg_color[1], bg_color[0])
            bbox = draw.textbbox(position, text, font=font)
            padding = 3
            draw.rectangle(
                [bbox[0] - padding, bbox[1] - padding, 
                 bbox[2] + padding, bbox[3] + padding],
                fill=rgb_bg_color
            )
        
        # 绘制文字
        draw.text(position, text, font=font, fill=rgb_color)
        
        # 转换回OpenCV图像 (RGB -> BGR)
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    
    def put_multiline_text(
        self, 
        image: np.ndarray, 
        lines: list,
        start_position: Tuple[int, int],
        font_size: int = 18,
        line_spacing: int = 25,
        color: Tuple[int, int, int] = (255, 255, 255),
        bg_color: Optional[Tuple[int, int, int]] = None
    ) -> np.ndarray:
        """
        在图像上绘制多行中文文字
        
        Args:
            image: OpenCV图像 (BGR格式)
            lines: 文字行列表，每行可以是字符串或(文字, 颜色)元组
            start_position: 起始位置 (x, y)
            font_size: 字体大小
            line_spacing: 行间距
            color: 默认文字颜色 (BGR格式)
            bg_color: 背景颜色 (BGR格式), None表示透明
            
        Returns:
            绘制后的图像
        """
        if image is None or not lines:
            return image
        
        output = image.copy()
        x, y = start_position
        
        for line in lines:
            if isinstance(line, tuple):
                text, line_color = line
            else:
                text = line
                line_color = color
            
            output = self.put_text(
                output, text, (x, y), 
                font_size=font_size, 
                color=line_color,
                bg_color=bg_color
            )
            y += line_spacing
        
        return output


# 全局实例
_text_renderer = None


def get_text_renderer() -> ChineseTextRenderer:
    """获取文字渲染器实例"""
    global _text_renderer
    if _text_renderer is None:
        _text_renderer = ChineseTextRenderer()
    return _text_renderer


def put_chinese_text(
    image: np.ndarray, 
    text: str, 
    position: Tuple[int, int],
    font_size: int = 20,
    color: Tuple[int, int, int] = (255, 255, 255),
    bg_color: Optional[Tuple[int, int, int]] = None
) -> np.ndarray:
    """便捷函数：在图像上绘制中文文字"""
    return get_text_renderer().put_text(
        image, text, position, font_size, color, bg_color
    )
