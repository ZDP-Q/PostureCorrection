"""
主控制器 - 姿态对比系统
"""

from typing import Optional, Tuple, Dict

import cv2
import numpy as np

from .config import Config
from .constants import LIMB_TO_ANGLES
from .models import PoseData
from .analyzer import PoseAnalyzer
from .detector import PoseDetector
from .renderer import PoseRenderer


class PoseComparisonSystem:
    """姿态对比系统主控制器"""
    
    def __init__(self):
        self.detector = PoseDetector()
        self.standard_pose: Optional[PoseData] = None
        self.reference_image: Optional[np.ndarray] = None
        self.renderer: Optional[PoseRenderer] = None
        
    def load_reference(self, image_path: str) -> bool:
        """
        加载参考图像并提取标准姿态
        
        Args:
            image_path: 参考图像路径
            
        Returns:
            是否成功
        """
        print(f"正在加载参考图像: {image_path}")
        
        self.reference_image = cv2.imread(image_path)
        if self.reference_image is None:
            print(f"错误：无法读取图像 {image_path}")
            return False
        
        self.standard_pose = self.detector.detect(self.reference_image)
        if self.standard_pose is None:
            print("错误：无法在参考图像中检测到姿态")
            return False
        
        print("参考姿态加载成功！")
        print("检测到的关节角度：")
        for name, angle in self.standard_pose.angles.items():
            if angle is not None:
                print(f"  {name}: {angle:.1f}°")
        
        return True
    
    def compare_poses(self, user_pose: PoseData) -> Tuple[Dict[str, bool], float]:
        """
        比较用户姿态与标准姿态
        
        Args:
            user_pose: 用户的姿态数据
            
        Returns:
            (各肢体段匹配结果, 总体匹配率)
        """
        if self.standard_pose is None:
            return {}, 0.0
        
        # 比较每个关节角度
        angle_matches = {}
        for name in self.standard_pose.angles:
            std_angle = self.standard_pose.angles.get(name)
            user_angle = user_pose.angles.get(name)
            matched, diff = PoseAnalyzer.compare_angles(std_angle, user_angle)
            angle_matches[name] = matched
        
        # 将角度匹配结果映射到肢体段
        limb_matches = {}
        for limb_name, related_angles in LIMB_TO_ANGLES.items():
            if not related_angles:
                limb_matches[limb_name] = True  # 没有相关角度的部分默认匹配
            else:
                # 所有相关角度都匹配才算该肢体匹配
                limb_matches[limb_name] = all(
                    angle_matches.get(angle_name, True) 
                    for angle_name in related_angles
                )
        
        # 计算总体匹配率
        valid_angles = [m for name, m in angle_matches.items() 
                       if self.standard_pose.angles.get(name) is not None]
        if valid_angles:
            match_ratio = sum(valid_angles) / len(valid_angles)
        else:
            match_ratio = 0.0
        
        return limb_matches, match_ratio
    
    def run(self, camera_id = 0, reference_path: Optional[str] = None):
        """
        运行姿态对比系统
        
        Args:
            camera_id: 摄像头ID 或 视频文件路径
            reference_path: 参考图像路径（可选）
        """
        # 加载参考图像
        if reference_path:
            if not self.load_reference(reference_path):
                print("警告：将在无参考模式下运行")
        
        # 打开视频源（摄像头或视频文件）
        is_video_file = isinstance(camera_id, str)
        cap = cv2.VideoCapture(camera_id)
        
        if not is_video_file:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, Config.CAMERA_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.CAMERA_HEIGHT)
        
        if not cap.isOpened():
            source_name = f"视频文件 {camera_id}" if is_video_file else "摄像头"
            print(f"错误：无法打开{source_name}")
            return
        
        # 获取实际分辨率
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) if is_video_file else 30
        frame_delay = int(1000 / fps) if fps > 0 else 33
        self.renderer = PoseRenderer(width, height)
        
        source_type = "视频" if is_video_file else "摄像头"
        print(f"\n=== 姿态对比系统已启动 ({source_type}模式) ===")
        print("按 'q' 退出")
        print("按 's' 截图保存当前姿态为参考")
        print("按 'r' 重新加载参考图像")
        print("按 '+'/'-' 调整角度阈值")
        if is_video_file:
            print("按 '空格' 暂停/继续")
        
        paused = False
        
        while True:
            if not paused:
                ret, frame = cap.read()
                if not ret:
                    if is_video_file:
                        # 视频播放完毕，循环播放
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue
                    else:
                        print("错误：无法读取摄像头画面")
                        break
            
            # 镜像翻转（摄像头模式更自然的交互）
            display_frame = frame.copy()
            if not is_video_file:
                display_frame = cv2.flip(display_frame, 1)
            
            # 检测用户姿态
            user_pose = self.detector.detect(display_frame)
            
            if user_pose:
                # 比较姿态
                if self.standard_pose:
                    limb_matches, match_ratio = self.compare_poses(user_pose)
                    
                    # 绘制带颜色反馈的骨架
                    display_frame = self.renderer.draw_skeleton(
                        display_frame, user_pose, limb_matches)
                    
                    # 叠加参考图
                    if self.reference_image is not None:
                        display_frame = self.renderer.overlay_reference(
                            display_frame, self.reference_image, self.standard_pose)
                    
                    # 绘制状态
                    display_frame = self.renderer.draw_status(display_frame, match_ratio)
                else:
                    # 无参考模式 - 只绘制骨架
                    display_frame = self.renderer.draw_skeleton(display_frame, user_pose)
                
                # 绘制角度信息
                display_frame = self.renderer.draw_angle_info(
                    display_frame, user_pose, self.standard_pose)
            else:
                # 未检测到姿态 - 使用中文文字渲染
                from src.utils.text_renderer import get_text_renderer
                text_renderer = get_text_renderer()
                display_frame = text_renderer.put_text(
                    display_frame, "未检测到姿态", (10, 30),
                    font_size=24, color=Config.COLOR_RED
                )
            
            # 显示帮助信息 (保持英文因为是快捷键提示)
            pause_hint = " SPACE:Pause" if is_video_file else ""
            help_text = f"Threshold: {Config.ANGLE_THRESHOLD:.0f}deg | Q:Quit S:Save R:Reload +/-:Threshold{pause_hint}"
            cv2.putText(display_frame, help_text, (10, height - 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, Config.COLOR_WHITE, 1)
            
            if paused:
                # 使用中文显示暂停
                from src.utils.text_renderer import get_text_renderer
                text_renderer = get_text_renderer()
                display_frame = text_renderer.put_text(
                    display_frame, "已暂停", (width // 2 - 50, 50),
                    font_size=32, color=Config.COLOR_YELLOW
                )
            
            # 显示画面
            cv2.imshow(Config.WINDOW_NAME, display_frame)
            
            # 处理按键
            key = cv2.waitKey(frame_delay) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord(' ') and is_video_file:
                paused = not paused
            elif key == ord('s'):
                # 保存当前帧为参考
                if user_pose:
                    cv2.imwrite("reference_pose.jpg", display_frame)
                    self.reference_image = display_frame.copy()
                    self.standard_pose = user_pose
                    print("已保存当前姿态为参考")
            elif key == ord('r'):
                # 重新加载参考图
                if reference_path:
                    self.load_reference(reference_path)
            elif key == ord('+') or key == ord('='):
                Config.ANGLE_THRESHOLD = min(45, Config.ANGLE_THRESHOLD + 5)
                print(f"角度阈值: {Config.ANGLE_THRESHOLD}°")
            elif key == ord('-'):
                Config.ANGLE_THRESHOLD = max(5, Config.ANGLE_THRESHOLD - 5)
                print(f"角度阈值: {Config.ANGLE_THRESHOLD}°")
        
        # 清理资源
        cap.release()
        cv2.destroyAllWindows()
        self.detector.close()
