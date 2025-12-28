"""
姿态对比应用核心逻辑
"""

from typing import Optional, Union

import cv2
import numpy as np

from src.deps import deps
from src.models import PoseData
from src.utils import VideoCapture, VideoSource, PoseRenderer


class PoseComparisonApp:
    """姿态对比应用"""
    
    def __init__(self):
        self._detector = None
        self._analyzer = None
        self._config = None
        self._renderer: Optional[PoseRenderer] = None
        
        self._standard_pose: Optional[PoseData] = None
        self._reference_image: Optional[np.ndarray] = None
    
    @property
    def detector(self):
        """懒加载检测器"""
        if self._detector is None:
            self._detector = deps.get_detector()
        return self._detector
    
    @property
    def analyzer(self):
        """懒加载分析器"""
        if self._analyzer is None:
            self._analyzer = deps.get_analyzer()
        return self._analyzer
    
    @property
    def config(self):
        """懒加载配置"""
        if self._config is None:
            self._config = deps.get_config()
        return self._config
    
    @property
    def standard_pose(self) -> Optional[PoseData]:
        """标准姿态"""
        return self._standard_pose
    
    @property
    def reference_image(self) -> Optional[np.ndarray]:
        """参考图像"""
        return self._reference_image
    
    def load_reference(self, image_path: str) -> bool:
        """
        加载参考图像并提取标准姿态
        
        Args:
            image_path: 参考图像路径
            
        Returns:
            是否成功
        """
        print(f"正在加载参考图像: {image_path}")
        
        self._reference_image = cv2.imread(image_path)
        if self._reference_image is None:
            print(f"错误：无法读取图像 {image_path}")
            return False
        
        self._standard_pose = self.detector.detect(self._reference_image)
        if self._standard_pose is None:
            print("错误：无法在参考图像中检测到姿态")
            return False
        
        print("参考姿态加载成功！")
        print("检测到的关节角度：")
        for name, angle in self._standard_pose.angles.items():
            if angle is not None:
                print(f"  {name}: {angle:.1f}°")
        
        return True
    
    def set_reference_pose(self, pose: PoseData, image: np.ndarray = None):
        """
        设置参考姿态
        
        Args:
            pose: 姿态数据
            image: 对应的图像（可选）
        """
        self._standard_pose = pose
        if image is not None:
            self._reference_image = image.copy()
    
    def compare_poses(self, user_pose: PoseData):
        """
        比较用户姿态与标准姿态
        
        Args:
            user_pose: 用户的姿态数据
            
        Returns:
            (各肢体段匹配结果, 总体匹配率)
        """
        if self._standard_pose is None:
            return {}, 0.0
        
        threshold = self.config.analyzer.angle_threshold
        return self.analyzer.compare_poses(
            self._standard_pose, 
            user_pose,
            threshold
        )
    
    def process_frame(self, frame: np.ndarray, flip: bool = False):
        """
        处理单帧图像
        
        Args:
            frame: 输入帧
            flip: 是否水平翻转
            
        Returns:
            (处理后的显示帧, 检测到的姿态, 匹配结果, 匹配率)
        """
        display_frame = frame.copy()
        if flip:
            display_frame = cv2.flip(display_frame, 1)
        
        # 初始化渲染器
        if self._renderer is None or \
           self._renderer.width != display_frame.shape[1] or \
           self._renderer.height != display_frame.shape[0]:
            self._renderer = PoseRenderer(
                display_frame.shape[1], 
                display_frame.shape[0],
                self.config
            )
        
        # 检测姿态
        user_pose = self.detector.detect(display_frame)
        limb_matches = {}
        match_ratio = 0.0
        
        if user_pose:
            # 比较姿态
            if self._standard_pose:
                limb_matches, match_ratio = self.compare_poses(user_pose)
                
                # 绘制带颜色反馈的骨架
                display_frame = self._renderer.draw_skeleton(
                    display_frame, user_pose, limb_matches)
                
                # 叠加参考图
                if self._reference_image is not None:
                    display_frame = self._renderer.overlay_reference(
                        display_frame, self._reference_image, self._standard_pose)
                
                # 绘制状态
                display_frame = self._renderer.draw_status(display_frame, match_ratio)
            else:
                # 无参考模式 - 只绘制骨架
                display_frame = self._renderer.draw_skeleton(display_frame, user_pose)
            
            # 绘制角度信息
            display_frame = self._renderer.draw_angle_info(
                display_frame, user_pose, self._standard_pose,
                self.config.analyzer.angle_threshold
            )
        else:
            # 未检测到姿态 - 使用中文文字渲染
            from src.utils.text_renderer import get_text_renderer
            text_renderer = get_text_renderer()
            display_frame = text_renderer.put_text(
                display_frame, "未检测到姿态", (10, 30),
                font_size=24, color=(0, 0, 255)
            )
        
        return display_frame, user_pose, limb_matches, match_ratio
    
    def run(
        self, 
        input_source: Union[int, str] = 0,
        reference_path: Optional[str] = None
    ):
        """
        运行姿态对比系统
        
        Args:
            input_source: 摄像头ID 或 视频文件路径
            reference_path: 参考图像路径（可选）
        """
        # 加载参考图像
        if reference_path:
            if not self.load_reference(reference_path):
                print("警告：将在无参考模式下运行")
        
        # 创建视频源
        if isinstance(input_source, str):
            source = VideoSource.from_file(input_source)
        else:
            source = VideoSource.from_camera(
                input_source,
                self.config.window.camera_width,
                self.config.window.camera_height
            )
        
        # 打开视频源
        with VideoCapture(source) as cap:
            if not cap.is_opened:
                print(f"错误：无法打开视频源")
                return
            
            source_type = "视频" if cap.is_video_file else "摄像头"
            print(f"\n=== 姿态对比系统已启动 ({source_type}模式) ===")
            print("按 'q' 退出")
            print("按 's' 截图保存当前姿态为参考")
            print("按 'r' 重新加载参考图像")
            print("按 '+'/'-' 调整角度阈值")
            if cap.is_video_file:
                print("按 '空格' 暂停/继续")
            
            paused = False
            frame = None
            
            while True:
                if not paused:
                    ret, frame = cap.read()
                    if not ret or frame is None:
                        continue
                
                # 处理帧
                display_frame, user_pose, _, _ = self.process_frame(
                    frame, 
                    flip=not cap.is_video_file
                )
                
                # 显示帮助信息
                pause_hint = " SPACE:Pause" if cap.is_video_file else ""
                threshold = self.config.analyzer.angle_threshold
                help_text = f"Threshold: {threshold:.0f}deg | Q:Quit S:Save R:Reload +/-:Threshold{pause_hint}"
                cv2.putText(display_frame, help_text, (10, cap.height - 70),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                if paused:
                    cv2.putText(display_frame, "PAUSED", (cap.width // 2 - 80, 50),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
                
                # 显示画面
                cv2.imshow(self.config.window.window_name, display_frame)
                
                # 处理按键
                key = cv2.waitKey(cap.frame_delay) & 0xFF
                
                if key == ord('q'):
                    break
                elif key == ord(' ') and cap.is_video_file:
                    paused = not paused
                elif key == ord('s'):
                    # 保存当前帧为参考
                    if user_pose:
                        cv2.imwrite("reference_pose.jpg", display_frame)
                        self.set_reference_pose(user_pose, display_frame)
                        print("已保存当前姿态为参考")
                elif key == ord('r'):
                    # 重新加载参考图
                    if reference_path:
                        self.load_reference(reference_path)
                elif key == ord('+') or key == ord('='):
                    new_threshold = min(45, threshold + 5)
                    self.config.set('analyzer.angle_threshold', new_threshold)
                    print(f"角度阈值: {new_threshold}°")
                elif key == ord('-'):
                    new_threshold = max(5, threshold - 5)
                    self.config.set('analyzer.angle_threshold', new_threshold)
                    print(f"角度阈值: {new_threshold}°")
        
        cv2.destroyAllWindows()
    
    def cleanup(self):
        """清理资源"""
        deps.cleanup()
