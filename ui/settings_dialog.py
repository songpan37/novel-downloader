"""Settings dialog for configuration - Modern Dark Theme"""

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QWidget, QCheckBox
)
from PySide6.QtCore import Qt

from core.config import ConfigManager, DEFAULT_CHROME_PATH


class SettingsDialog(QDialog):
    """Settings configuration dialog with modern dark UI"""

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.config = config_manager.load()
        self.init_ui()

    def init_ui(self):
        """Initialize the dialog UI"""
        self.setWindowTitle("设置")
        self.setMinimumSize(520, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
                background-color: #1a1a1a;
            }
            QLineEdit {
                background-color: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px 12px;
                color: #e0e0e0;
            }
            QLineEdit:focus {
                border-color: #606060;
            }
            QLineEdit:disabled {
                background-color: #252525;
                color: #808080;
            }
            QPushButton {
                background-color: #3a3a3a;
                border: 1px solid #505050;
                border-radius: 4px;
                padding: 6px 12px;
                color: #e0e0e0;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
            QCheckBox {
                color: #e0e0e0;
                background-color: #1a1a1a;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid #505050;
                background-color: #2a2a2a;
            }
            QCheckBox::indicator:checked {
                background-color: #4a7c4a;
                border-color: #4a7c4a;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # ===== Storage Directory =====
        storage_label = QLabel("存储目录")
        storage_label.setStyleSheet("color: #e0e0e0; font-size: 14px; font-weight: bold; background-color: #1a1a1a;")
        layout.addWidget(storage_label)

        dir_row = QHBoxLayout()
        dir_row.setContentsMargins(0, 0, 0, 0)
        self.root_dir_input = QLineEdit()
        self.root_dir_input.setText(self.config.root_dir)
        self.root_dir_input.setPlaceholderText("选择小说存储目录...")
        dir_row.addWidget(self.root_dir_input, 1)

        self.browse_btn = QPushButton("浏览")
        self.browse_btn.setFixedWidth(80)
        self.browse_btn.clicked.connect(self.on_browse)
        dir_row.addWidget(self.browse_btn)
        layout.addLayout(dir_row)

        # Spacer
        layout.addSpacing(8)

        # ===== Plugin URLs =====
        plugin_label = QLabel("插件地址")
        plugin_label.setStyleSheet("color: #e0e0e0; font-size: 14px; font-weight: bold; background-color: #1a1a1a;")
        layout.addWidget(plugin_label)

        plugin_desc = QLabel("设置各插件的网站地址（留空使用默认地址）")
        plugin_desc.setStyleSheet("color: #808080; font-size: 12px; background-color: #1a1a1a;")
        layout.addWidget(plugin_desc)

        # 3yt plugin URL
        url_3yt_row = QHBoxLayout()
        url_3yt_row.setContentsMargins(0, 0, 0, 0)
        url_3yt_label = QLabel("3yt:")
        url_3yt_label.setFixedWidth(50)
        url_3yt_label.setStyleSheet("color: #e0e0e0; background-color: #1a1a1a;")
        url_3yt_row.addWidget(url_3yt_label)
        self.url_3yt = QLineEdit()
        self.url_3yt.setPlaceholderText("https://www.3yt.com/")
        self.url_3yt.setText(self.config.plugin_urls.get('3yt', ''))
        url_3yt_row.addWidget(self.url_3yt, 1)
        layout.addLayout(url_3yt_row)

        # 92yq plugin URL
        url_92yq_row = QHBoxLayout()
        url_92yq_row.setContentsMargins(0, 0, 0, 0)
        url_92yq_label = QLabel("92yq:")
        url_92yq_label.setFixedWidth(50)
        url_92yq_label.setStyleSheet("color: #e0e0e0; background-color: #1a1a1a;")
        url_92yq_row.addWidget(url_92yq_label)
        self.url_92yq = QLineEdit()
        self.url_92yq.setPlaceholderText("https://www.92yq.com/")
        self.url_92yq.setText(self.config.plugin_urls.get('92yq', ''))
        url_92yq_row.addWidget(self.url_92yq, 1)
        layout.addLayout(url_92yq_row)

        # bqg plugin URL
        url_bqg_row = QHBoxLayout()
        url_bqg_row.setContentsMargins(0, 0, 0, 0)
        url_bqg_label = QLabel("bqg:")
        url_bqg_label.setFixedWidth(50)
        url_bqg_label.setStyleSheet("color: #e0e0e0; background-color: #1a1a1a;")
        url_bqg_row.addWidget(url_bqg_label)
        self.url_bqg = QLineEdit()
        self.url_bqg.setPlaceholderText("https://www.bqg655.cc/")
        self.url_bqg.setText(self.config.plugin_urls.get('bqg', ''))
        url_bqg_row.addWidget(self.url_bqg, 1)
        layout.addLayout(url_bqg_row)

        # Spacer
        layout.addSpacing(8)

        # ===== Browser Mode =====
        browser_label = QLabel("浏览器模式")
        browser_label.setStyleSheet("color: #e0e0e0; font-size: 14px; font-weight: bold; background-color: #1a1a1a;")
        layout.addWidget(browser_label)

        self.headless_checkbox = QCheckBox("无头模式（不显示浏览器窗口）")
        self.headless_checkbox.setChecked(self.config.browser_headless)
        self.headless_checkbox.setStyleSheet("color: #e0e0e0; background-color: #1a1a1a;")
        layout.addWidget(self.headless_checkbox)

        # Chrome path
        chrome_label = QLabel("Chrome 路径")
        chrome_label.setStyleSheet("color: #e0e0e0; font-size: 13px; background-color: #1a1a1a;")
        layout.addWidget(chrome_label)

        chrome_row = QHBoxLayout()
        chrome_row.setContentsMargins(0, 0, 0, 0)
        self.chrome_path_input = QLineEdit()
        default_chrome = self.config.chrome_path if self.config.chrome_path else DEFAULT_CHROME_PATH
        self.chrome_path_input.setText(self.config.chrome_path)
        self.chrome_path_input.setPlaceholderText(DEFAULT_CHROME_PATH)
        self.chrome_path_input.textChanged.connect(self.on_chrome_path_changed)
        chrome_row.addWidget(self.chrome_path_input, 1)

        self.chrome_browse_btn = QPushButton("浏览")
        self.chrome_browse_btn.setFixedWidth(80)
        self.chrome_browse_btn.clicked.connect(self.on_chrome_browse)
        chrome_row.addWidget(self.chrome_browse_btn)
        layout.addLayout(chrome_row)

        self.chrome_status_label = QLabel("")
        self.chrome_status_label.setStyleSheet("color: #808080; font-size: 12px; background-color: #1a1a1a;")
        layout.addWidget(self.chrome_status_label)

        # Check initial chrome path
        self.check_chrome_path()

        # Spacer
        layout.addStretch()

        # ===== Dialog Buttons =====
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setFixedWidth(100)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("保存")
        self.save_btn.setFixedWidth(100)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a7c4a;
                border: none;
                color: white;
            }
            QPushButton:hover {
                background-color: #5a9c5a;
            }
        """)
        self.save_btn.clicked.connect(self.on_save)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)

    def on_browse(self):
        """Handle browse button click"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "选择存储目录", self.root_dir_input.text()
        )
        if dir_path:
            self.root_dir_input.setText(dir_path)

    def on_chrome_browse(self):
        """Handle chrome browse button click"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 Chrome 可执行文件",
            self.chrome_path_input.text() or DEFAULT_CHROME_PATH,
            "Executable (*.exe)"
        )
        if file_path:
            self.chrome_path_input.setText(file_path)

    def on_chrome_path_changed(self, text):
        """Handle chrome path text change"""
        self.check_chrome_path()

    def check_chrome_path(self):
        """Check if chrome path is valid and update status label"""
        path = self.chrome_path_input.text().strip()
        if not path:
            path = DEFAULT_CHROME_PATH

        if os.path.exists(path):
            self.chrome_status_label.setText("✓ Chrome 路径有效")
            self.chrome_status_label.setStyleSheet("color: #4a9f4a; font-size: 12px; background-color: #1a1a1a;")
        else:
            self.chrome_status_label.setText("✗ Chrome 路径无效或文件不存在")
            self.chrome_status_label.setStyleSheet("color: #ff6b6b; font-size: 12px; background-color: #1a1a1a;")

    def on_save(self):
        """Save settings and close"""
        # Update root dir
        new_root_dir = self.root_dir_input.text().strip()
        self.config_manager.set_root_dir(new_root_dir)

        # Update config
        config = self.config_manager.load()
        config.browser_headless = self.headless_checkbox.isChecked()
        config.chrome_path = self.chrome_path_input.text().strip()

        plugin_urls = {}
        if self.url_3yt.text().strip():
            plugin_urls['3yt'] = self.url_3yt.text().strip()
        if self.url_92yq.text().strip():
            plugin_urls['92yq'] = self.url_92yq.text().strip()
        if self.url_bqg.text().strip():
            plugin_urls['bqg'] = self.url_bqg.text().strip()

        config.plugin_urls = plugin_urls
        self.config_manager.save(config)

        self.accept()