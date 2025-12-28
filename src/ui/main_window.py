"""
主窗口
"""

from typing import Optional

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QMessageBox, QAction, QMenuBar, QStatusBar
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

from .video_widget import VideoWidget
from .control_panel import ControlPanel
from src.app import PoseComparisonApp


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._app = PoseComparisonApp()
        self._timer: Optional[QTimer] = None
        self._is_running = False
        
        self._init_ui()
        self._init_menu()
        self._connect_signals()
    
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("姿态对比系统 - Pose Comparison System")
        self.setMinimumSize(1200, 700)
        
        # 创建中心widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # 使用分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧控制面板
        self.control_panel = ControlPanel()
        self.control_panel.setFixedWidth(280)
        splitter.addWidget(self.control_panel)
        
        # 右侧视频显示区域
        self.video_widget = VideoWidget()
        splitter.addWidget(self.video_widget)
        
        # 设置分割比例
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        # 状态栏
        self.statusBar().showMessage("就绪")
        
        # 定时器用于视频更新
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_frame)
        
        # 应用默认深色主题
        self._apply_main_theme(True)
    
    def _init_menu(self):
        """初始化菜单"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        open_ref_action = QAction("打开参考图像(&O)", self)
        open_ref_action.setShortcut("Ctrl+O")
        open_ref_action.triggered.connect(self._on_open_reference)
        file_menu.addAction(open_ref_action)
        
        save_action = QAction("保存当前帧(&S)", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._on_save_frame)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")
        
        self.show_skeleton_action = QAction("显示骨架", self, checkable=True)
        self.show_skeleton_action.setChecked(True)
        view_menu.addAction(self.show_skeleton_action)
        
        self.show_angles_action = QAction("显示角度信息", self, checkable=True)
        self.show_angles_action.setChecked(True)
        view_menu.addAction(self.show_angles_action)
        
        self.show_reference_action = QAction("显示参考图", self, checkable=True)
        self.show_reference_action.setChecked(True)
        view_menu.addAction(self.show_reference_action)
        
        view_menu.addSeparator()
        
        # 主题切换菜单项
        self.dark_theme_action = QAction("深色主题", self, checkable=True)
        self.dark_theme_action.setChecked(True)
        self.dark_theme_action.triggered.connect(self._on_menu_theme_changed)
        view_menu.addAction(self.dark_theme_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
    
    def _connect_signals(self):
        """连接信号"""
        # 控制面板信号
        self.control_panel.start_clicked.connect(self._on_start)
        self.control_panel.pause_clicked.connect(self._on_pause)
        self.control_panel.exit_clicked.connect(self.close)
        self.control_panel.reference_changed.connect(self._on_reference_changed)
        self.control_panel.source_changed.connect(self._on_source_changed)
        self.control_panel.model_changed.connect(self._on_model_changed)
        self.control_panel.threshold_changed.connect(self._on_threshold_changed)
        self.control_panel.theme_changed.connect(self._on_theme_changed)
    
    def _on_start(self):
        """开始按钮点击"""
        if self._is_running:
            return
        
        # 获取视频源配置
        source_config = self.control_panel.get_source_config()
        
        if source_config['type'] == 'camera':
            from src.utils import VideoSource
            source = VideoSource.from_camera(source_config['camera_id'])
        else:
            from src.utils import VideoSource
            if not source_config['video_path']:
                QMessageBox.warning(self, "警告", "请选择视频文件")
                return
            source = VideoSource.from_file(source_config['video_path'])
        
        # 初始化视频widget
        if not self.video_widget.start_capture(source):
            QMessageBox.critical(self, "错误", "无法打开视频源")
            return
        
        self._is_running = True
        self._timer.start(33)  # ~30fps
        
        self.control_panel.set_running_state(True)
        self.statusBar().showMessage("运行中...")
    
    def _on_pause(self):
        """暂停/继续按钮点击"""
        if not self._is_running:
            return
        
        if self._timer.isActive():
            self._timer.stop()
            self.control_panel.set_paused_state(True)
            self.statusBar().showMessage("已暂停")
        else:
            self._timer.start(33)
            self.control_panel.set_paused_state(False)
            self.statusBar().showMessage("运行中...")
    
    def _on_stop(self):
        """停止"""
        self._is_running = False
        self._timer.stop()
        self.video_widget.stop_capture()
        self.control_panel.set_running_state(False)
        self.statusBar().showMessage("已停止")
    
    def _update_frame(self):
        """更新帧"""
        if not self._is_running:
            return
        
        # 读取帧
        ret, frame = self.video_widget.read_frame()
        if not ret or frame is None:
            return
        
        # 处理帧
        display_frame, pose, limb_matches, match_ratio = self._app.process_frame(
            frame, 
            flip=not self.video_widget.is_video_file
        )
        
        # 显示帧
        self.video_widget.display_frame(display_frame)
        
        # 更新状态
        if pose:
            self.statusBar().showMessage(f"匹配率: {match_ratio*100:.1f}%")
            self.control_panel.update_match_ratio(match_ratio)
        else:
            self.statusBar().showMessage("未检测到姿态")
    
    def _on_reference_changed(self, path: str):
        """参考图像改变"""
        if path:
            if self._app.load_reference(path):
                self.statusBar().showMessage(f"已加载参考图像: {path}")
            else:
                QMessageBox.warning(self, "警告", f"无法加载参考图像: {path}")
    
    def _on_source_changed(self):
        """视频源改变"""
        if self._is_running:
            self._on_stop()
    
    def _on_model_changed(self, model_name: str):
        """模型改变"""
        from src.deps import deps
        try:
            deps.select_detector(model_name)
            deps.reset_instance('detector', model_name)
            self.statusBar().showMessage(f"已切换模型: {model_name}")
        except Exception as e:
            QMessageBox.warning(self, "警告", f"切换模型失败: {e}")
    
    def _on_threshold_changed(self, value: float):
        """阈值改变"""
        self._app.config.set('analyzer.angle_threshold', value)
    
    def _on_open_reference(self):
        """打开参考图像"""
        from PyQt5.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(
            self, "选择参考图像", "",
            "图像文件 (*.jpg *.jpeg *.png *.bmp);;所有文件 (*.*)"
        )
        if path:
            self.control_panel.set_reference_path(path)
            self._on_reference_changed(path)
    
    def _on_save_frame(self):
        """保存当前帧"""
        frame = self.video_widget.get_current_frame()
        if frame is None:
            QMessageBox.warning(self, "警告", "没有可保存的帧")
            return
        
        from PyQt5.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            self, "保存帧", "frame.jpg",
            "JPEG图像 (*.jpg);;PNG图像 (*.png);;所有文件 (*.*)"
        )
        if path:
            import cv2
            cv2.imwrite(path, frame)
            self.statusBar().showMessage(f"已保存: {path}")
    
    def _on_about(self):
        """关于对话框"""
        QMessageBox.about(
            self,
            "关于姿态对比系统",
            """<h2>姿态对比系统</h2>
            <p>版本: 2.0.0</p>
            <p>使用 OpenCV + MediaPipe 实现实时姿态检测与参考姿态对比</p>
            <p>支持：</p>
            <ul>
                <li>实时摄像头/视频文件输入</li>
                <li>姿态检测与骨架可视化</li>
                <li>与参考姿态对比</li>
                <li>关节角度分析</li>
                <li>深色/浅色主题切换</li>
            </ul>
            """
        )
    
    def _on_theme_changed(self, is_dark: bool):
        """主题切换 (来自控制面板)"""
        self.dark_theme_action.setChecked(is_dark)
        self._apply_main_theme(is_dark)
    
    def _on_menu_theme_changed(self, checked: bool):
        """主题切换 (来自菜单)"""
        self.control_panel.set_theme(checked)
        self._apply_main_theme(checked)
    
    def _apply_main_theme(self, is_dark: bool):
        """应用主窗口主题"""
        if is_dark:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1a1a2e;
                }
                QMenuBar {
                    background-color: #2d2d44;
                    color: #e0e0e0;
                }
                QMenuBar::item:selected {
                    background-color: #3a3a5c;
                }
                QMenu {
                    background-color: #2d2d44;
                    color: #e0e0e0;
                }
                QMenu::item:selected {
                    background-color: #3a3a5c;
                }
                QStatusBar {
                    background-color: #2d2d44;
                    color: #e0e0e0;
                }
            """)
            self.video_widget.set_dark_theme(True)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f5f5f5;
                }
                QMenuBar {
                    background-color: #ffffff;
                    color: #333333;
                }
                QMenuBar::item:selected {
                    background-color: #e0e0e0;
                }
                QMenu {
                    background-color: #ffffff;
                    color: #333333;
                }
                QMenu::item:selected {
                    background-color: #e0e0e0;
                }
                QStatusBar {
                    background-color: #ffffff;
                    color: #333333;
                }
            """)
            self.video_widget.set_dark_theme(False)
    
    def set_reference_image(self, path: str):
        """设置参考图像（用于命令行传参）"""
        self.control_panel.set_reference_path(path)
        self._on_reference_changed(path)
    
    def closeEvent(self, event):
        """关闭事件"""
        self._on_stop()
        self._app.cleanup()
        event.accept()
