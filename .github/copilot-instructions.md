# 姿态对比系统 (Pose Comparison System) - AI Agent Guide

## 项目概述
基于 OpenCV + MediaPipe + PyQt5 的实时姿态检测与对比系统。核心技术是**归一化角度计算**——将骨骼坐标转换为关节角度，消除距离差异，实现精确的姿态匹配。

## 架构核心：依赖注入 + 插件系统

### 三层架构模式
```
src/core/         → 抽象基类 (BaseDetector, BaseAnalyzer, BaseConfig)
src/deps/         → DI容器 + 具体实现 (MediaPipeDetector, DefaultAnalyzer)
src/app.py        → 应用逻辑（懒加载依赖）
```

### 依赖注入机制 (关键！)
- **单例容器**: `deps = Deps()` 是全局单例
- **懒加载**: 组件首次访问时才初始化（使用 `LazyInstance` 包装器）
- **自动注册**: 具体实现类通过 `is_default = True` 类属性自动注册
- **获取组件**: 
  ```python
  detector = deps.get_detector()  # 获取默认或指定检测器
  analyzer = deps.get_analyzer()
  config = deps.get_config()
  ```

**重要**: 新增检测器或分析器时，必须：
1. 继承对应的 `Base*` 抽象类（在 `src/core/`）
2. 在类中设置 `is_default = True/False` 属性
3. 放在 `src/deps/` 目录下会自动注册

### 现有实现类
- **检测器**: `MediaPipeDetector` (lite, 默认), `MediaPipeFullDetector`, `MediaPipeHeavyDetector`
- **分析器**: `DefaultAnalyzer` (基于关节角度)
- **配置**: `DefaultConfig`

## 数据流与核心算法

### 1. 参考姿态提取
```python
reference_image → detector.detect() → PoseData(landmarks, angles)
```
- 33个骨骼点 (`Landmark`: x, y, z, visibility)
- 预计算关节角度 (肩、肘、髋、膝等)

### 2. 实时帧处理
```python
camera_frame → detector.detect() → user_pose
→ analyzer.compare_poses(standard_pose, user_pose)
→ (match_results: Dict[str, bool], score: float)
```

### 3. 角度归一化计算（核心技术）
**为什么**: 直接比较坐标受距离影响，角度比较更鲁棒

实现在 `src/deps/default_analyzer.py`:
```python
def calculate_angle(p1, p2, p3):
    # p2为顶点，计算p1-p2-p3的夹角
    v1 = p1 - p2
    v2 = p3 - p2
    angle = arccos(v1·v2 / |v1||v2|)  # 向量点积
```

**关键关节**: 定义在 `src/constants.py` 的 `ANGLE_JOINTS`
- 肩膀角度: 大臂与躯干
- 肘部角度: 大臂与小臂
- 髋部角度: 大腿与躯干
- 膝盖角度: 大腿与小腿

## 运行模式与入口

### 命令行模式
```bash
python -m src.main                    # 仅显示骨架
python -m src.main -r ref.jpg         # 加载参考图
python -m src.main --video test.mp4   # 处理视频
```

### GUI模式（推荐）
```bash
python -m src.main --gui
```
- 主窗口: `src/ui/main_window.py` (PyQt5)
- 控制面板: `src/ui/control_panel.py`
- 视频显示: `src/ui/video_widget.py`

### 开发调试
```bash
python -m src.main --gui --mode dev  # 开启DEBUG日志
```

## 视觉渲染系统

### 配色逻辑 (src/utils/renderer.py)
- 🟢 **绿色**: 角度匹配 (阈值 15° 内)
- 🔴 **红色加粗**: 角度不匹配 (超过阈值)
- 🟡 **黄色**: 参考姿态骨架

### 骨架连接
定义在 `src/constants.py` 的 `SKELETON_CONNECTIONS` (13条骨骼线段):
```python
(LEFT_SHOULDER, LEFT_ELBOW, "左大臂")
(LEFT_ELBOW, LEFT_WRIST, "左小臂")
# ... 躯干、腿部等
```

### 参考图叠加
- 半透明叠加在右上角
- 可调参数: `OVERLAY_ALPHA = 0.4`, `OVERLAY_SCALE = 0.3`

## 项目约定

### 文件组织
- **不要修改** `src/core/` 的抽象类（除非扩展新功能）
- **新组件放** `src/deps/` 并继承 `Base*` 类
- **工具函数放** `src/utils/`（已有 video, renderer, helpers, feedback）

### 命名约定
- 检测器类名: `*Detector` (如 `MediaPipeDetector`)
- 分析器类名: `*Analyzer` (如 `DefaultAnalyzer`)
- 私有方法: `_method_name`
- 配置常量: 全大写 `ANGLE_THRESHOLD`

### 代码风格
- Black格式化: `line_length = 100`
- 类型注解: 必须标注返回类型和参数类型
- 文档字符串: 必须有 Args/Returns 说明

## 常见任务

### 添加新检测模型
1. 在 `src/deps/` 创建 `xxx_detector.py`
2. 继承 `BaseDetector`
3. 实现 `detect()`, `initialize()`, `name`, `description`
4. 设置 `is_default = True/False`
5. 无需手动注册，DI容器会自动发现

### 修改角度匹配逻辑
编辑 `src/deps/default_analyzer.py` 的 `compare_angles()` 或 `extract_pose_angles()`

### 添加新关节角度
1. 在 `src/constants.py` 的 `ANGLE_JOINTS` 添加定义
2. 分析器会自动计算（无需修改代码）

### 调整视觉效果
修改 `src/config.py` 或 `src/utils/renderer.py` 的配色/线条参数

## 依赖管理

### 环境设置
```bash
# 推荐使用 uv（已有 uv.lock）
uv sync

# 或 pip
pip install -e .
```

### 关键依赖版本
- Python: 3.9-3.12
- PyQt5: 5.15.9（固定版本，避免兼容问题）
- NumPy: <2.0.0（MediaPipe要求）
- MediaPipe: >=0.10.0

### 模型文件
- Lite模型: `pose_landmarker.task` (根目录，首次自动下载)
- Heavy模型: `models/pose_landmarker_heavy.task`

## 故障排查

### 常见错误
1. **"无法检测到姿态"**: 检查参考图是否包含完整人体，调低 `MIN_DETECTION_CONFIDENCE`
2. **PyQt5导入失败**: 确保版本为 5.15.9，Windows可能需要 `PyQt5-Qt5==5.15.2`
3. **模型下载失败**: 手动下载 `.task` 文件并放到正确位置

### 调试技巧
- 开启dev模式查看详细日志: `--mode dev`
- 检查依赖注入状态: `deps.list_components('detector')`
- 查看骨骼点可见性: `pose.landmarks[i].visibility`
