"""
人性化姿态反馈生成器

将角度差异转换为简单易懂的身体部位调整提示
"""

from typing import List, Tuple
from src.models import PoseData


class FeedbackGenerator:
    """人性化反馈生成器"""
    
    # 角度名称到身体部位的映射
    ANGLE_TO_BODY_PART = {
        "左肩角度": "左手臂",
        "右肩角度": "右手臂", 
        "左肘角度": "左手肘",
        "右肘角度": "右手肘",
        "左髋角度": "左腿",
        "右髋角度": "右腿",
        "左膝角度": "左膝盖",
        "右膝角度": "右膝盖",
    }
    
    # 调整方向提示
    ADJUSTMENT_TIPS = {
        "左肩角度": {
            "increase": "把左手臂抬高一点",
            "decrease": "把左手臂放低一点",
        },
        "右肩角度": {
            "increase": "把右手臂抬高一点", 
            "decrease": "把右手臂放低一点",
        },
        "左肘角度": {
            "increase": "伸直左手肘一点",
            "decrease": "弯曲左手肘一点",
        },
        "右肘角度": {
            "increase": "伸直右手肘一点",
            "decrease": "弯曲右手肘一点",
        },
        "左髋角度": {
            "increase": "左腿向前伸一点",
            "decrease": "左腿向后收一点",
        },
        "右髋角度": {
            "increase": "右腿向前伸一点",
            "decrease": "右腿向后收一点",
        },
        "左膝角度": {
            "increase": "伸直左腿一点",
            "decrease": "弯曲左膝盖一点",
        },
        "右膝角度": {
            "increase": "伸直右腿一点",
            "decrease": "弯曲右膝盖一点",
        },
    }
    
    def __init__(self, angle_threshold: float = 15.0):
        """
        初始化反馈生成器
        
        Args:
            angle_threshold: 角度容差阈值
        """
        self.angle_threshold = angle_threshold
    
    def generate_feedback(
        self, 
        user_pose: PoseData, 
        standard_pose: PoseData
    ) -> List[Tuple[str, Tuple[int, int, int]]]:
        """
        生成人性化的姿态调整反馈
        
        Args:
            user_pose: 用户姿态
            standard_pose: 标准姿态
            
        Returns:
            反馈列表，每项为 (反馈文字, BGR颜色)
        """
        feedback_list = []
        
        # 颜色定义 (BGR)
        color_green = (0, 255, 0)
        color_red = (0, 0, 255)
        color_yellow = (0, 255, 255)
        
        errors = []
        correct_count = 0
        
        for angle_name in user_pose.angles:
            user_angle = user_pose.angles.get(angle_name)
            std_angle = standard_pose.angles.get(angle_name)
            
            if user_angle is None or std_angle is None:
                continue
            
            diff = user_angle - std_angle
            abs_diff = abs(diff)
            
            if abs_diff <= self.angle_threshold:
                correct_count += 1
            else:
                # 需要调整
                body_part = self.ANGLE_TO_BODY_PART.get(angle_name, angle_name)
                tips = self.ADJUSTMENT_TIPS.get(angle_name, {})
                
                if diff > 0:
                    # 用户角度大于标准，需要减小
                    tip = tips.get("decrease", f"调整{body_part}")
                else:
                    # 用户角度小于标准，需要增大
                    tip = tips.get("increase", f"调整{body_part}")
                
                # 根据偏差程度选择颜色
                if abs_diff > 30:
                    color = color_red
                    urgency = "⚠ "
                else:
                    color = color_yellow
                    urgency = "→ "
                
                errors.append((urgency + tip, color))
        
        # 添加总体状态
        total_angles = len([a for a in user_pose.angles.values() if a is not None])
        if total_angles > 0:
            ratio = correct_count / total_angles
            if ratio >= 0.9:
                feedback_list.append(("✓ 姿势很标准！", color_green))
            elif ratio >= 0.7:
                feedback_list.append(("○ 姿势基本正确，微调一下", color_yellow))
            else:
                feedback_list.append(("✗ 需要调整姿势", color_red))
        
        # 只显示最重要的3个调整建议
        feedback_list.extend(errors[:3])
        
        if not errors and correct_count > 0:
            feedback_list.append(("保持住！", color_green))
        
        return feedback_list
    
    def get_simple_status(
        self, 
        user_pose: PoseData, 
        standard_pose: PoseData
    ) -> Tuple[str, Tuple[int, int, int]]:
        """
        获取简单的状态提示
        
        Returns:
            (状态文字, BGR颜色)
        """
        color_green = (0, 255, 0)
        color_red = (0, 0, 255)
        color_yellow = (0, 255, 255)
        
        correct_count = 0
        total_count = 0
        
        for angle_name in user_pose.angles:
            user_angle = user_pose.angles.get(angle_name)
            std_angle = standard_pose.angles.get(angle_name)
            
            if user_angle is None or std_angle is None:
                continue
            
            total_count += 1
            if abs(user_angle - std_angle) <= self.angle_threshold:
                correct_count += 1
        
        if total_count == 0:
            return ("检测中...", color_yellow)
        
        ratio = correct_count / total_count
        
        if ratio >= 0.9:
            return ("很棒！姿势标准", color_green)
        elif ratio >= 0.7:
            return ("还不错，继续调整", color_yellow)
        elif ratio >= 0.5:
            return ("需要调整姿势", color_yellow)
        else:
            return ("姿势差异较大", color_red)


# 全局实例
_feedback_generator = None


def get_feedback_generator(threshold: float = 15.0) -> FeedbackGenerator:
    """获取反馈生成器实例"""
    global _feedback_generator
    if _feedback_generator is None or _feedback_generator.angle_threshold != threshold:
        _feedback_generator = FeedbackGenerator(threshold)
    return _feedback_generator
