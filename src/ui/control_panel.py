"""
控制面板组件
"""

from typing import Dict, Any

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QComboBox, QSlider, QSpinBox,
    QLineEdit, QFileDialog, QRadioButton, QButtonGroup,
    QProgressBar, QFrame, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal


# 深色主题样式
DARK_STYLE = """
    QWidget#controlPanel {
        background-color: #1e1e2e;
    }
    QGroupBox {
        font-weight: bold;
        font-size: 12px;
        border: 1px solid #3a3a5c;
        border-radius: 6px;
        margin-top: 16px;
        padding: 12px 8px 8px 8px;
        background-color: #2d2d44;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 10px;
        top: 4px;
        padding: 0 5px;
        color: #e0e0e0;
        background-color: #2d2d44;
    }
    QPushButton {
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: bold;
        background-color: #3a3a5c;
        color: #e0e0e0;
        border: none;
    }
    QPushButton:hover {
        background-color: #4a4a6c;
    }
    QPushButton#startBtn {
        background-color: #4CAF50;
        color: white;
    }
    QPushButton#startBtn:hover {
        background-color: #45a049;
    }
    QPushButton#startBtn:disabled {
        background-color: #666;
    }
    QPushButton#pauseBtn {
        background-color: #ff9800;
        color: white;
    }
    QPushButton#pauseBtn:hover {
        background-color: #e68900;
    }
    QPushButton#exitBtn {
        background-color: #f44336;
        color: white;
    }
    QPushButton#exitBtn:hover {
        background-color: #d32f2f;
    }
    QComboBox, QLineEdit, QSpinBox {
        padding: 5px;
        border: 1px solid #3a3a5c;
        border-radius: 4px;
        background-color: #1a1a2e;
        color: #e0e0e0;
    }
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid #e0e0e0;
        margin-right: 5px;
    }
    QSlider::groove:horizontal {
        border: 1px solid #3a3a5c;
        height: 8px;
        background: #1a1a2e;
        border-radius: 4px;
    }
    QSlider::handle:horizontal {
        background: #4CAF50;
        width: 16px;
        margin: -4px 0;
        border-radius: 8px;
    }
    QLabel {
        color: #e0e0e0;
    }
    QRadioButton {
        color: #e0e0e0;
        spacing: 8px;
    }
    QRadioButton::indicator {
        width: 14px;
        height: 14px;
    }
    QCheckBox {
        color: #e0e0e0;
        spacing: 8px;
    }
    QCheckBox::indicator {
        width: 16px;
        height: 16px;
    }
"""

# 浅色主题样式
LIGHT_STYLE = """
    QWidget#controlPanel {
        background-color: #f5f5f5;
    }
    QGroupBox {
        font-weight: bold;
        font-size: 12px;
        border: 1px solid #cccccc;
        border-radius: 6px;
        margin-top: 16px;
        padding: 12px 8px 8px 8px;
        background-color: #ffffff;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 10px;
        top: 4px;
        padding: 0 5px;
        color: #333333;
        background-color: #ffffff;
    }
    QPushButton {
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: bold;
        background-color: #e0e0e0;
        color: #333333;
        border: 1px solid #cccccc;
    }
    QPushButton:hover {
        background-color: #d0d0d0;
    }
    QPushButton#startBtn {
        background-color: #4CAF50;
        color: white;
        border: none;
    }
    QPushButton#startBtn:hover {
        background-color: #45a049;
    }
    QPushButton#startBtn:disabled {
        background-color: #aaaaaa;
    }
    QPushButton#pauseBtn {
        background-color: #ff9800;
        color: white;
        border: none;
    }
    QPushButton#pauseBtn:hover {
        background-color: #e68900;
    }
    QPushButton#exitBtn {
        background-color: #f44336;
        color: white;
        border: none;
    }
    QPushButton#exitBtn:hover {
        background-color: #d32f2f;
    }
    QComboBox, QLineEdit, QSpinBox {
        padding: 5px;
        border: 1px solid #cccccc;
        border-radius: 4px;
        background-color: #ffffff;
        color: #333333;
    }
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid #333333;
        margin-right: 5px;
    }
    QSlider::groove:horizontal {
        border: 1px solid #cccccc;
        height: 8px;
        background: #e0e0e0;
        border-radius: 4px;
    }
    QSlider::handle:horizontal {
        background: #4CAF50;
        width: 16px;
        margin: -4px 0;
        border-radius: 8px;
    }
    QLabel {
        color: #333333;
    }
    QRadioButton {
        color: #333333;
        spacing: 8px;
    }
    QRadioButton::indicator {
        width: 14px;
        height: 14px;
    }
    QCheckBox {
        color: #333333;
        spacing: 8px;
    }
    QCheckBox::indicator {
        width: 16px;
        height: 16px;
    }
"""


class ControlPanel(QWidget):
    """控制面板"""
    
    # 信号
    start_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    exit_clicked = pyqtSignal()
    reference_changed = pyqtSignal(str)
    source_changed = pyqtSignal()
    model_changed = pyqtSignal(str)
    threshold_changed = pyqtSignal(float)
    theme_changed = pyqtSignal(bool)  # True为深色，False为浅色
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("controlPanel")
        
        self._is_dark_theme = True
        self._init_ui()
        self._load_models()
        self._apply_theme()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # 主题切换
        theme_layout = QHBoxLayout()
        theme_label = QLabel("🌙 深色模式")
        theme_label.setObjectName("themeLabel")
        self.theme_checkbox = QCheckBox()
        self.theme_checkbox.setChecked(True)
        self.theme_checkbox.stateChanged.connect(self._on_theme_changed)
        theme_layout.addWidget(theme_label)
        theme_layout.addStretch()
        theme_layout.addWidget(self.theme_checkbox)
        layout.addLayout(theme_layout)
        
        # 模型选择
        model_group = QGroupBox("模型选择")
        model_layout = QVBoxLayout(model_group)
        model_layout.setContentsMargins(8, 8, 8, 8)
        
        self.model_combo = QComboBox()
        self.model_combo.currentTextChanged.connect(
            lambda text: self.model_changed.emit(text)
        )
        model_layout.addWidget(self.model_combo)
        
        layout.addWidget(model_group)
        
        # 参考图像
        ref_group = QGroupBox("参考图像")
        ref_layout = QVBoxLayout(ref_group)
        ref_layout.setContentsMargins(8, 8, 8, 8)
        
        ref_input_layout = QHBoxLayout()
        self.ref_path_edit = QLineEdit()
        self.ref_path_edit.setPlaceholderText("选择参考图像...")
        self.ref_path_edit.setReadOnly(True)
        ref_input_layout.addWidget(self.ref_path_edit)
        
        self.browse_btn = QPushButton("浏览")
        self.browse_btn.clicked.connect(self._on_browse_reference)
        ref_input_layout.addWidget(self.browse_btn)
        
        ref_layout.addLayout(ref_input_layout)
        
        layout.addWidget(ref_group)
        
        # 输入源选择
        source_group = QGroupBox("输入源")
        source_layout = QVBoxLayout(source_group)
        source_layout.setContentsMargins(8, 8, 8, 8)
        
        # 摄像头/视频选择
        source_type_layout = QHBoxLayout()
        self.source_button_group = QButtonGroup(self)
        
        self.camera_radio = QRadioButton("摄像头")
        self.camera_radio.setChecked(True)
        self.camera_radio.toggled.connect(self._on_source_type_changed)
        self.source_button_group.addButton(self.camera_radio)
        source_type_layout.addWidget(self.camera_radio)
        
        self.video_radio = QRadioButton("视频文件")
        self.video_radio.toggled.connect(self._on_source_type_changed)
        self.source_button_group.addButton(self.video_radio)
        source_type_layout.addWidget(self.video_radio)
        
        source_layout.addLayout(source_type_layout)
        
        # 摄像头ID
        camera_layout = QHBoxLayout()
        camera_layout.addWidget(QLabel("摄像头ID:"))
        self.camera_id_spin = QSpinBox()
        self.camera_id_spin.setRange(0, 10)
        self.camera_id_spin.setValue(0)
        camera_layout.addWidget(self.camera_id_spin)
        camera_layout.addStretch()
        source_layout.addLayout(camera_layout)
        
        # 视频文件路径
        video_layout = QHBoxLayout()
        self.video_path_edit = QLineEdit()
        self.video_path_edit.setPlaceholderText("选择视频文件...")
        self.video_path_edit.setReadOnly(True)
        self.video_path_edit.setEnabled(False)
        video_layout.addWidget(self.video_path_edit)
        
        self.video_browse_btn = QPushButton("浏览")
        self.video_browse_btn.clicked.connect(self._on_browse_video)
        self.video_browse_btn.setEnabled(False)
        video_layout.addWidget(self.video_browse_btn)
        
        source_layout.addLayout(video_layout)
        
        layout.addWidget(source_group)
        
        # 参数配置
        params_group = QGroupBox("参数配置")
        params_layout = QVBoxLayout(params_group)
        params_layout.setContentsMargins(8, 8, 8, 8)
        
        # 角度阈值
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("角度阈值:"))
        
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(5, 45)
        self.threshold_slider.setValue(15)
        self.threshold_slider.valueChanged.connect(self._on_threshold_changed)
        threshold_layout.addWidget(self.threshold_slider)
        
        self.threshold_label = QLabel("15°")
        self.threshold_label.setFixedWidth(35)
        threshold_layout.addWidget(self.threshold_label)
        
        params_layout.addLayout(threshold_layout)
        
        layout.addWidget(params_group)
        
        # 匹配率显示
        match_group = QGroupBox("匹配状态")
        match_layout = QVBoxLayout(match_group)
        match_layout.setContentsMargins(8, 8, 8, 8)
        
        self.match_progress = QProgressBar()
        self.match_progress.setRange(0, 100)
        self.match_progress.setValue(0)
        self.match_progress.setFormat("%v%")
        match_layout.addWidget(self.match_progress)
        
        self.match_label = QLabel("等待开始...")
        self.match_label.setAlignment(Qt.AlignCenter)
        match_layout.addWidget(self.match_label)
        
        layout.addWidget(match_group)
        
        # 添加弹性空间
        layout.addStretch()
        
        # 控制按钮
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("开始")
        self.start_btn.setObjectName("startBtn")
        self.start_btn.clicked.connect(self.start_clicked.emit)
        btn_layout.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("暂停")
        self.pause_btn.setObjectName("pauseBtn")
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.pause_clicked.emit)
        btn_layout.addWidget(self.pause_btn)
        
        layout.addLayout(btn_layout)
        
        # 退出按钮
        self.exit_btn = QPushButton("退出")
        self.exit_btn.setObjectName("exitBtn")
        self.exit_btn.clicked.connect(self.exit_clicked.emit)
        layout.addWidget(self.exit_btn)
    
    def _apply_theme(self):
        """应用主题"""
        if self._is_dark_theme:
            self.setStyleSheet(DARK_STYLE)
            self._update_progress_bar_style("#4CAF50")
        else:
            self.setStyleSheet(LIGHT_STYLE)
            self._update_progress_bar_style("#4CAF50")
        
        # 更新主题标签
        theme_label = self.findChild(QLabel, "themeLabel")
        if theme_label:
            if self._is_dark_theme:
                theme_label.setText("🌙 深色模式")
            else:
                theme_label.setText("☀️ 浅色模式")
    
    def _update_progress_bar_style(self, color: str):
        """更新进度条样式"""
        if self._is_dark_theme:
            self.match_progress.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid #3a3a5c;
                    border-radius: 4px;
                    text-align: center;
                    background-color: #1a1a2e;
                    color: #e0e0e0;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 3px;
                }}
            """)
        else:
            self.match_progress.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    text-align: center;
                    background-color: #e0e0e0;
                    color: #333333;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 3px;
                }}
            """)
    
    def _on_theme_changed(self, state: int):
        """主题切换"""
        self._is_dark_theme = state == Qt.Checked
        self._apply_theme()
        self.theme_changed.emit(self._is_dark_theme)
    
    def _load_models(self):
        """加载可用模型列表"""
        from src.deps import deps
        
        models = deps.list_detectors()
        self.model_combo.clear()
        for name, desc in models.items():
            self.model_combo.addItem(name)
    
    def _on_browse_reference(self):
        """浏览参考图像"""
        path, _ = QFileDialog.getOpenFileName(
            self, "选择参考图像", "",
            "图像文件 (*.jpg *.jpeg *.png *.bmp);;所有文件 (*.*)"
        )
        if path:
            self.ref_path_edit.setText(path)
            self.reference_changed.emit(path)
    
    def _on_browse_video(self):
        """浏览视频文件"""
        path, _ = QFileDialog.getOpenFileName(
            self, "选择视频文件", "",
            "视频文件 (*.mp4 *.avi *.mkv *.mov);;所有文件 (*.*)"
        )
        if path:
            self.video_path_edit.setText(path)
            self.source_changed.emit()
    
    def _on_source_type_changed(self, checked: bool):
        """输入源类型改变"""
        is_video = self.video_radio.isChecked()
        
        self.camera_id_spin.setEnabled(not is_video)
        self.video_path_edit.setEnabled(is_video)
        self.video_browse_btn.setEnabled(is_video)
        
        self.source_changed.emit()
    
    def _on_threshold_changed(self, value: int):
        """阈值改变"""
        self.threshold_label.setText(f"{value}°")
        self.threshold_changed.emit(float(value))
    
    def get_source_config(self) -> Dict[str, Any]:
        """获取视频源配置"""
        if self.camera_radio.isChecked():
            return {
                'type': 'camera',
                'camera_id': self.camera_id_spin.value()
            }
        else:
            return {
                'type': 'video',
                'video_path': self.video_path_edit.text()
            }
    
    def set_reference_path(self, path: str):
        """设置参考图像路径"""
        self.ref_path_edit.setText(path)
    
    def set_running_state(self, running: bool):
        """设置运行状态"""
        self.start_btn.setEnabled(not running)
        self.pause_btn.setEnabled(running)
        
        if not running:
            self.pause_btn.setText("暂停")
            self.match_progress.setValue(0)
            self.match_label.setText("等待开始...")
    
    def set_paused_state(self, paused: bool):
        """设置暂停状态"""
        if paused:
            self.pause_btn.setText("继续")
        else:
            self.pause_btn.setText("暂停")
    
    def update_match_ratio(self, ratio: float):
        """更新匹配率"""
        percentage = int(ratio * 100)
        self.match_progress.setValue(percentage)
        
        if ratio >= 0.7:
            status = "优秀"
            color = "#4CAF50"
        elif ratio >= 0.4:
            status = "良好"
            color = "#ff9800"
        else:
            status = "需改进"
            color = "#f44336"
        
        self.match_label.setText(f"{status} ({percentage}%)")
        self._update_progress_bar_style(color)
    
    @property
    def is_dark_theme(self) -> bool:
        """是否为深色主题"""
        return self._is_dark_theme
    
    def set_theme(self, is_dark: bool):
        """设置主题"""
        self._is_dark_theme = is_dark
        self.theme_checkbox.setChecked(is_dark)
        self._apply_theme()
