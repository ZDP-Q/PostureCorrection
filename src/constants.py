"""
骨骼连接定义和常量
"""

from enum import Enum


class PoseLandmark(Enum):
    """MediaPipe 骨骼点枚举"""
    NOSE = 0
    LEFT_EYE_INNER = 1
    LEFT_EYE = 2
    LEFT_EYE_OUTER = 3
    RIGHT_EYE_INNER = 4
    RIGHT_EYE = 5
    RIGHT_EYE_OUTER = 6
    LEFT_EAR = 7
    RIGHT_EAR = 8
    MOUTH_LEFT = 9
    MOUTH_RIGHT = 10
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_PINKY = 17
    RIGHT_PINKY = 18
    LEFT_INDEX = 19
    RIGHT_INDEX = 20
    LEFT_THUMB = 21
    RIGHT_THUMB = 22
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_HEEL = 29
    RIGHT_HEEL = 30
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32


# 骨骼连接段定义 - 用于绘制和角度计算
SKELETON_CONNECTIONS = [
    # 躯干
    (PoseLandmark.LEFT_SHOULDER, PoseLandmark.RIGHT_SHOULDER, "躯干上"),
    (PoseLandmark.LEFT_HIP, PoseLandmark.RIGHT_HIP, "躯干下"),
    (PoseLandmark.LEFT_SHOULDER, PoseLandmark.LEFT_HIP, "左侧躯干"),
    (PoseLandmark.RIGHT_SHOULDER, PoseLandmark.RIGHT_HIP, "右侧躯干"),
    
    # 左臂
    (PoseLandmark.LEFT_SHOULDER, PoseLandmark.LEFT_ELBOW, "左大臂"),
    (PoseLandmark.LEFT_ELBOW, PoseLandmark.LEFT_WRIST, "左小臂"),
    
    # 右臂
    (PoseLandmark.RIGHT_SHOULDER, PoseLandmark.RIGHT_ELBOW, "右大臂"),
    (PoseLandmark.RIGHT_ELBOW, PoseLandmark.RIGHT_WRIST, "右小臂"),
    
    # 左腿
    (PoseLandmark.LEFT_HIP, PoseLandmark.LEFT_KNEE, "左大腿"),
    (PoseLandmark.LEFT_KNEE, PoseLandmark.LEFT_ANKLE, "左小腿"),
    
    # 右腿
    (PoseLandmark.RIGHT_HIP, PoseLandmark.RIGHT_KNEE, "右大腿"),
    (PoseLandmark.RIGHT_KNEE, PoseLandmark.RIGHT_ANKLE, "右小腿"),
]

# 需要计算角度的关节点（关节点, 连接点1, 连接点2, 名称）
ANGLE_JOINTS = [
    # 肩膀角度（大臂与躯干的夹角）
    (PoseLandmark.LEFT_SHOULDER, PoseLandmark.LEFT_ELBOW, PoseLandmark.LEFT_HIP, "左肩角度"),
    (PoseLandmark.RIGHT_SHOULDER, PoseLandmark.RIGHT_ELBOW, PoseLandmark.RIGHT_HIP, "右肩角度"),
    
    # 肘部角度
    (PoseLandmark.LEFT_ELBOW, PoseLandmark.LEFT_SHOULDER, PoseLandmark.LEFT_WRIST, "左肘角度"),
    (PoseLandmark.RIGHT_ELBOW, PoseLandmark.RIGHT_SHOULDER, PoseLandmark.RIGHT_WRIST, "右肘角度"),
    
    # 髋部角度（大腿与躯干的夹角）
    (PoseLandmark.LEFT_HIP, PoseLandmark.LEFT_KNEE, PoseLandmark.LEFT_SHOULDER, "左髋角度"),
    (PoseLandmark.RIGHT_HIP, PoseLandmark.RIGHT_KNEE, PoseLandmark.RIGHT_SHOULDER, "右髋角度"),
    
    # 膝盖角度
    (PoseLandmark.LEFT_KNEE, PoseLandmark.LEFT_HIP, PoseLandmark.LEFT_ANKLE, "左膝角度"),
    (PoseLandmark.RIGHT_KNEE, PoseLandmark.RIGHT_HIP, PoseLandmark.RIGHT_ANKLE, "右膝角度"),
]

# 肢体段与相关角度的映射
LIMB_TO_ANGLES = {
    "左大臂": ["左肩角度", "左肘角度"],
    "左小臂": ["左肘角度"],
    "右大臂": ["右肩角度", "右肘角度"],
    "右小臂": ["右肘角度"],
    "左大腿": ["左髋角度", "左膝角度"],
    "左小腿": ["左膝角度"],
    "右大腿": ["右髋角度", "右膝角度"],
    "右小腿": ["右膝角度"],
    "左侧躯干": ["左肩角度", "左髋角度"],
    "右侧躯干": ["右肩角度", "右髋角度"],
    "躯干上": [],
    "躯干下": [],
}
