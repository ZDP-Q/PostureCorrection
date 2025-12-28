"""
工具函数
"""

import cv2

from .config import Config
from .detector import PoseDetector
from .renderer import PoseRenderer


def create_sample_reference():
    """创建示例参考图像（用于测试）"""
    print("正在创建示例参考图像...")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头")
        return
    
    detector = PoseDetector()
    
    print("请摆好姿势，按空格键捕获参考姿态...")
    
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
            cv2.putText(frame, "Press SPACE to capture, Q to quit", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, Config.COLOR_GREEN, 2)
        
        cv2.imshow("Capture Reference", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' ') and pose:
            cv2.imwrite("reference_pose.jpg", frame)
            print("参考姿态已保存到 reference_pose.jpg")
            break
        elif key == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    detector.close()
