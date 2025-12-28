"""
系统配置参数
"""


class Config:
    """系统配置参数"""
    # MediaPipe 配置
    MIN_DETECTION_CONFIDENCE = 0.5
    MIN_TRACKING_CONFIDENCE = 0.5
    
    # 角度匹配阈值（度数）
    ANGLE_THRESHOLD = 15.0  # 角度差小于此值认为匹配
    
    # 颜色定义 (BGR格式)
    COLOR_GREEN = (0, 255, 0)      # 匹配 - 绿色
    COLOR_RED = (0, 0, 255)        # 不匹配 - 红色
    COLOR_YELLOW = (0, 255, 255)   # 参考骨架 - 黄色
    COLOR_WHITE = (255, 255, 255)  # 白色
    
    # 线条粗细
    LINE_THICKNESS_NORMAL = 2
    LINE_THICKNESS_BOLD = 4
    
    # 参考图叠加配置
    OVERLAY_ALPHA = 0.4  # 半透明度
    OVERLAY_SCALE = 0.3  # 参考图缩放比例
    
    # 窗口配置
    WINDOW_NAME = "Pose Comparison System"
    CAMERA_WIDTH = 1280
    CAMERA_HEIGHT = 720
