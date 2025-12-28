"""
辅助工具函数
"""

import cv2
from typing import Optional


def create_sample_reference(output_path: str = "reference_pose.jpg") -> Optional[str]:
    """
    创建示例参考图像（用于测试）
    
    Args:
        output_path: 输出文件路径
        
    Returns:
        保存的文件路径，失败返回None
    """
    from src.deps import deps
    from src.utils.renderer import PoseRenderer
    
    print("正在创建示例参考图像...")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头")
        return None
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    detector = deps.get_detector()
    config = deps.get_config()
    
    print("请摆好姿势，按空格键捕获参考姿态...")
    
    saved_path = None
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        pose = detector.detect(frame)
        
        if pose:
            # 绘制骨架预览
            renderer = PoseRenderer(frame.shape[1], frame.shape[0])
            frame = renderer.draw_skeleton(frame, pose)
            # 使用中文渲染
            from .text_renderer import get_text_renderer
            text_renderer = get_text_renderer()
            frame = text_renderer.put_text(
                frame, "按空格键捕获参考姿态，按Q退出", (10, 30),
                font_size=18, color=(0, 255, 0)
            )
        
        cv2.imshow("Capture Reference", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' ') and pose:
            cv2.imwrite(output_path, frame)
            print(f"参考姿态已保存到 {output_path}")
            saved_path = output_path
            break
        elif key == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    return saved_path


def load_image(image_path: str):
    """
    加载图像
    
    Args:
        image_path: 图像文件路径
        
    Returns:
        图像数组或None
    """
    image = cv2.imread(image_path)
    if image is None:
        print(f"错误：无法读取图像 {image_path}")
    return image


def save_image(image, output_path: str) -> bool:
    """
    保存图像
    
    Args:
        image: 图像数组
        output_path: 输出文件路径
        
    Returns:
        是否成功
    """
    try:
        cv2.imwrite(output_path, image)
        return True
    except Exception as e:
        print(f"保存图像失败: {e}")
        return False
