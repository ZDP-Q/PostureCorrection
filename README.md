# 姿态对比系统 (Pose Comparison System)

基于 **OpenCV + MediaPipe + PyQt5** 的实时姿态检测与对比系统。

## 功能特性

### 核心功能
- **参考图预处理**：加载参考图像，使用 MediaPipe 提取 33 个骨骼坐标点作为 `Standard_Pose`
- **实时流处理**：打开摄像头或视频文件，每帧提取用户的 `User_Pose`
- **归一化角度计算**：将坐标转换为"肢体向量角度"，消除距离差异的影响
- **依赖注入架构**：支持灵活切换不同的检测模型和分析器

### 视觉反馈 UI
- **Qt5图形界面**：提供现代化的用户界面
- 参考图半透明叠加在画面右上角
- 在用户身上绘制骨架线
- **红/绿色机制**：
  - 🟢 **绿色**：角度匹配，骨骼线显示为绿色
  - 🔴 **红色加粗**：角度不匹配，骨骼线显示为红色并加粗
- 实时显示匹配百分比进度条

## 项目结构

```
src/
├── core/           # 抽象基类
│   ├── base_detector.py    # 关键点识别模型抽象类
│   ├── base_config.py      # 配置抽象类
│   └── base_analyzer.py    # 姿势分析器抽象类
├── deps/           # 依赖注入
│   ├── deps.py             # 依赖注入容器
│   ├── registry.py         # 组件注册表
│   ├── mediapipe_detector.py  # MediaPipe检测器实现
│   ├── default_analyzer.py    # 默认分析器实现
│   └── default_config.py      # 默认配置实现
├── utils/          # 工具类
│   ├── video.py            # 视频捕获工具
│   ├── renderer.py         # 姿态渲染器
│   └── helpers.py          # 辅助函数
├── ui/             # Qt5界面
│   ├── main_window.py      # 主窗口
│   ├── video_widget.py     # 视频显示组件
│   └── control_panel.py    # 控制面板
├── main.py         # 主入口
├── app.py          # 应用核心逻辑
├── models.py       # 数据模型
└── constants.py    # 常量定义
```

## 技术原理

### 归一化计算（关键技术）

直接比对 (x, y) 坐标存在问题：人站的远近不同会导致坐标差异很大。

**解决方案**：将坐标转换为"肢体向量角度"

```
向量角度计算公式：
v1 = p1 - p_joint  (从关节点到点1的向量)
v2 = p2 - p_joint  (从关节点到点2的向量)
角度 = arccos(v1·v2 / |v1||v2|)
```

计算的关节角度包括：
- **肩膀角度**：大臂与躯干的夹角
- **肘部角度**：大臂与小臂的夹角
- **髋部角度**：大腿与躯干的夹角
- **膝盖角度**：大腿与小腿的夹角

## 安装

### 依赖项
- Python >= 3.9
- OpenCV >= 4.8.0
- MediaPipe >= 0.10.0
- NumPy >= 1.24.0
- PyQt5 >= 5.15.0

### 安装步骤

```bash
# 创建虚拟环境（可选）
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install opencv-python mediapipe numpy PyQt5
```

## 使用方法

### 启动方式

#### 1. 命令行模式

```bash
# 直接运行（无参考图，仅显示骨架）
python -m src.main

# 使用参考图像
python -m src.main -r reference_pose.jpg

# 指定摄像头
python -m src.main -c 0 -r reference_pose.jpg

# 使用视频文件
python -m src.main -v video.mp4 -r reference_pose.jpg
```

#### 2. 图形界面模式

```bash
# 启动Qt5图形界面
python -m src.main --gui

# 开发模式（显示详细日志）
python -m src.main --mode dev --gui

# 发布模式
python -m src.main --mode release --gui
```

### 运行模式

| 模式 | 说明 |
|------|------|
| `dev` | 开发模式，显示详细日志 |
| `release` | 发布模式，仅显示警告和错误 |
| `test` | 测试模式，用于自动化测试 |

### 捕获参考姿态

```bash
# 进入捕获模式
python -m src.main --capture
```
摆好姿势后按空格键保存参考姿态。

### 命令行快捷键

| 按键 | 功能 |
|------|------|
| `Q` | 退出程序 |
| `S` | 保存当前姿态为参考 |
| `R` | 重新加载参考图像 |
| `+` | 增加角度阈值（更宽松） |
| `-` | 减少角度阈值（更严格） |
| `空格` | 暂停/继续（视频文件模式） |

## 扩展开发

### 添加新的检测器

1. 在 `src/deps/` 目录下创建新的检测器文件
2. 继承 `BaseDetector` 抽象类
3. 实现所有抽象方法
4. 设置 `is_default = True` 使其成为默认检测器（可选）

```python
from src.core import BaseDetector

class MyCustomDetector(BaseDetector):
    is_default = False  # 设置为True则为默认
    
    @property
    def name(self) -> str:
        return "MyCustomDetector"
    
    @property
    def description(self) -> str:
        return "自定义检测器"
    
    def initialize(self) -> bool:
        # 初始化逻辑
        return True
    
    def detect(self, image):
        # 检测逻辑
        pass
    
    # ... 实现其他抽象方法
```

### 使用依赖注入

```python
from src.deps import deps

# 获取检测器
detector = deps.get_detector()

# 获取分析器
analyzer = deps.get_analyzer()

# 获取配置
config = deps.get_config()

# 列出可用检测器
print(deps.list_detectors())

# 切换检测器
deps.select_detector("MyCustomDetector")
```

## 代码结构说明

### 主要类

1. **`BaseDetector`** - 检测器抽象基类
   - `detect()`: 检测图像中的姿态
   - `detect_batch()`: 批量检测

2. **`BaseAnalyzer`** - 分析器抽象基类
   - `calculate_angle()`: 计算三点夹角
   - `extract_pose_angles()`: 提取所有关节角度
   - `compare_poses()`: 比较姿态差异

3. **`BaseConfig`** - 配置抽象基类
   - 提供统一的配置接口

4. **`Deps`** - 依赖注入容器
   - 自动发现和注册组件
   - 支持懒加载
   - 提供统一的组件访问接口
   - `overlay_reference()`: 叠加参考图
   - `draw_status()`: 绘制匹配状态

4. **`PoseComparisonSystem`** - 主控制器
   - `load_reference()`: 加载参考姿态
   - `compare_poses()`: 比较姿态
   - `run()`: 运行主循环

## 配置参数

在 `Config` 类中可调整：

```python
ANGLE_THRESHOLD = 15.0  # 角度匹配阈值（度数）
OVERLAY_ALPHA = 0.4     # 参考图透明度
OVERLAY_SCALE = 0.3     # 参考图缩放比例
```

## 效果展示

运行程序后：
1. 摄像头画面实时显示
2. 右上角显示参考姿态（半透明黄色骨架）
3. 用户身上显示彩色骨架
4. 底部显示匹配进度条
5. 左侧显示各关节角度详情

## License

MIT License
