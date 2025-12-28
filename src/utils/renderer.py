"""
姿态可视化渲染器
"""

from typing import Optional, Tuple, Dict

import cv2
import numpy as np

from src.models import Landmark, PoseData
from src.constants import SKELETON_CONNECTIONS
from .text_renderer import get_text_renderer
from .feedback import get_feedback_generator


class PoseRenderer:
    """姿态可视化渲染器"""
    
    def __init__(self, width: int, height: int, config=None):
        """
        初始化渲染器
        
        Args:
            width: 画面宽度
            height: 画面高度
            config: 配置对象（可选）
        """
        self.width = width
        self.height = height
        self._config = config
        
        # 默认颜色配置 (BGR)
        self.color_green = (0, 255, 0)
        self.color_red = (0, 0, 255)
        self.color_yellow = (0, 255, 255)
        self.color_white = (255, 255, 255)
        
        # 默认线条配置
        self.line_thickness_normal = 2
        self.line_thickness_bold = 4
        
        # 默认叠加配置
        self.overlay_alpha = 0.4
        self.overlay_scale = 0.3
        
        self._load_config()
    
    def _load_config(self):
        """从配置加载参数"""
        if self._config is not None:
            colors = self._config.colors
            self.color_green = colors.green
            self.color_red = colors.red
            self.color_yellow = colors.yellow
            self.color_white = colors.white
            
            render = self._config.render
            self.line_thickness_normal = render.line_thickness_normal
            self.line_thickness_bold = render.line_thickness_bold
            self.overlay_alpha = render.overlay_alpha
            self.overlay_scale = render.overlay_scale
    
    def landmark_to_pixel(self, lm: Landmark) -> Tuple[int, int]:
        """将归一化坐标转换为像素坐标"""
        x = int(lm.x * self.width)
        y = int(lm.y * self.height)
        return (x, y)
    
    def draw_skeleton(
        self, 
        image: np.ndarray, 
        pose: PoseData,
        comparison_results: Optional[Dict[str, bool]] = None,
        is_reference: bool = False
    ) -> np.ndarray:
        """
        绘制骨架
        
        Args:
            image: 背景图像
            pose: 姿态数据
            comparison_results: 各肢体段的匹配结果
            is_reference: 是否是参考骨架
            
        Returns:
            绘制后的图像
        """
        output = image.copy()
        
        for start_lm, end_lm, name in SKELETON_CONNECTIONS:
            start_point = pose.landmarks[start_lm.value]
            end_point = pose.landmarks[end_lm.value]
            
            # 检查可见性
            if start_point.visibility < 0.5 or end_point.visibility < 0.5:
                continue
            
            # 获取像素坐标
            start_px = self.landmark_to_pixel(start_point)
            end_px = self.landmark_to_pixel(end_point)
            
            # 确定颜色和粗细
            if is_reference:
                color = self.color_yellow
                thickness = self.line_thickness_normal
            elif comparison_results is not None and name in comparison_results:
                if comparison_results[name]:
                    color = self.color_green
                    thickness = self.line_thickness_normal
                else:
                    color = self.color_red
                    thickness = self.line_thickness_bold
            else:
                color = self.color_white
                thickness = self.line_thickness_normal
            
            # 绘制线段
            cv2.line(output, start_px, end_px, color, thickness)
        
        # 绘制关节点
        for i, lm in enumerate(pose.landmarks):
            if lm.visibility > 0.5:
                px = self.landmark_to_pixel(lm)
                cv2.circle(output, px, 4, self.color_white, -1)
        
        return output
    
    def draw_angle_info(
        self, 
        image: np.ndarray, 
        pose: PoseData,
        standard_pose: Optional[PoseData] = None,
        threshold: float = 15.0
    ) -> np.ndarray:
        """
        绘制人性化的姿态调整提示
        
        不再显示角度数值，而是显示简单易懂的调整建议
        """
        output = image.copy()
        
        if standard_pose is None:
            # 无参考姿势时，显示简单提示
            text_renderer = get_text_renderer()
            output = text_renderer.put_text(
                output, "请加载参考姿势", (10, 30),
                font_size=18, color=self.color_yellow
            )
            return output
        
        # 获取人性化反馈
        feedback_gen = get_feedback_generator(threshold)
        feedback_list = feedback_gen.generate_feedback(pose, standard_pose)
        
        # 使用中文文字渲染器绘制反馈
        text_renderer = get_text_renderer()
        output = text_renderer.put_multiline_text(
            output,
            feedback_list,
            start_position=(10, 30),
            font_size=18,
            line_spacing=25
        )
        
        return output
    
    def overlay_reference(
        self, 
        image: np.ndarray, 
        ref_image: np.ndarray,
        ref_pose: PoseData
    ) -> np.ndarray:
        """
        将参考图半透明叠加到画面角落
        
        Args:
            image: 主画面
            ref_image: 参考图像
            ref_pose: 参考姿态数据
            
        Returns:
            叠加后的图像
        """
        output = image.copy()
        
        # 缩放参考图
        new_width = int(ref_image.shape[1] * self.overlay_scale)
        new_height = int(ref_image.shape[0] * self.overlay_scale)
        ref_small = cv2.resize(ref_image, (new_width, new_height))
        
        # 在缩放后的参考图上绘制骨架
        small_renderer = PoseRenderer(new_width, new_height)
        ref_small = small_renderer.draw_skeleton(ref_small, ref_pose, is_reference=True)
        
        # 添加边框
        cv2.rectangle(ref_small, (0, 0), (new_width-1, new_height-1), 
                     self.color_yellow, 2)
        
        # 叠加到右上角
        x_offset = output.shape[1] - new_width - 10
        y_offset = 10
        
        # 创建ROI
        roi = output[y_offset:y_offset+new_height, x_offset:x_offset+new_width]
        
        # 半透明混合
        blended = cv2.addWeighted(roi, 1 - self.overlay_alpha, 
                                  ref_small, self.overlay_alpha, 0)
        output[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = blended
        
        # 添加标签 (使用中文)
        text_renderer = get_text_renderer()
        output = text_renderer.put_text(
            output, "参考姿势", (x_offset, y_offset - 8),
            font_size=16, color=self.color_yellow
        )
        
        return output
    
    def draw_status(self, image: np.ndarray, match_ratio: float) -> np.ndarray:
        """绘制匹配状态"""
        output = image.copy()
        
        # 计算匹配百分比
        percentage = match_ratio * 100
        
        # 状态栏背景
        cv2.rectangle(output, (10, image.shape[0] - 60), 
                     (300, image.shape[0] - 10), (0, 0, 0), -1)
        
        # 进度条
        bar_width = int(250 * match_ratio)
        bar_color = self.color_green if match_ratio > 0.7 else (
            self.color_yellow if match_ratio > 0.4 else self.color_red
        )
        cv2.rectangle(output, (20, image.shape[0] - 50), 
                     (20 + bar_width, image.shape[0] - 30), bar_color, -1)
        cv2.rectangle(output, (20, image.shape[0] - 50), 
                     (270, image.shape[0] - 30), self.color_white, 1)
        
        # 使用中文显示匹配状态
        text_renderer = get_text_renderer()
        if match_ratio >= 0.9:
            status_text = f"匹配度: {percentage:.0f}% - 很棒！"
        elif match_ratio >= 0.7:
            status_text = f"匹配度: {percentage:.0f}% - 不错"
        elif match_ratio >= 0.5:
            status_text = f"匹配度: {percentage:.0f}% - 继续调整"
        else:
            status_text = f"匹配度: {percentage:.0f}% - 加油"
        
        output = text_renderer.put_text(
            output, status_text, (20, image.shape[0] - 12),
            font_size=14, color=self.color_white
        )
        
        return output
    
    def draw_text(
        self, 
        image: np.ndarray, 
        text: str, 
        position: Tuple[int, int],
        color: Tuple[int, int, int] = None,
        font_scale: float = 0.7,
        thickness: int = 2,
        use_chinese: bool = True
    ) -> np.ndarray:
        """
        绘制文字（支持中文）
        
        Args:
            image: 图像
            text: 文字内容
            position: 位置 (x, y)
            color: 颜色 (BGR)
            font_scale: 字体缩放（仅英文有效）
            thickness: 线条粗细（仅英文有效）
            use_chinese: 是否使用中文渲染
        """
        output = image.copy()
        if color is None:
            color = self.color_white
        
        if use_chinese:
            text_renderer = get_text_renderer()
            font_size = int(font_scale * 25)  # 转换字体大小
            output = text_renderer.put_text(
                output, text, position, font_size=font_size, color=color
            )
        else:
            cv2.putText(output, text, position, cv2.FONT_HERSHEY_SIMPLEX, 
                       font_scale, color, thickness)
        return output
