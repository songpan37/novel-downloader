"""Settings dialog for configuration - Modern Dark Theme"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QListWidget, QFileDialog, QWidget
)
from PySide6.QtCore import Qt

from core.config import ConfigManager
from ui.theme import get_stylesheet, COLORS, SPACING, RADIUS, FONT_SIZES


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
        self.setMinimumSize(480, 400)
        self.setStyleSheet(get_stylesheet())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])

        # Title
        title = QLabel("⚙ 设置")
        title.setStyleSheet(f"""
            color: {COLORS["text_primary"]};
            font-size: {FONT_SIZES["xl"]}px;
            font-weight: bold;
        """)
        layout.addWidget(title)

        # ===== Storage Directory Section =====
        storage_section = QWidget()
        storage_section.setStyleSheet(f"""
            background-color: {COLORS["bg_secondary"]};
            border-radius: {RADIUS["lg"]}px;
            padding: {SPACING["md"]}px;
        """)
        storage_layout = QVBoxLayout(storage_section)
        storage_layout.setContentsMargins(SPACING["md"], SPACING["md"], SPACING["md"], SPACING["md"])
        storage_layout.setSpacing(SPACING["md"])

        storage_title = QLabel("📁 存储目录")
        storage_title.setStyleSheet(f"""
            color: {COLORS["text_primary"]};
            font-size: {FONT_SIZES["md"]}px;
            font-weight: bold;
        """)
        storage_layout.addWidget(storage_title)

        dir_row = QHBoxLayout()
        self.root_dir_input = QLineEdit()
        self.root_dir_input.setText(self.config.root_dir)
        self.root_dir_input.setPlaceholderText("选择小说存储目录...")
        dir_row.addWidget(self.root_dir_input, 1)

        self.browse_btn = QPushButton("浏览")
        self.browse_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["bg_tertiary"]};
                border: 1px solid {COLORS["border"]};
                border-radius: {RADIUS["md"]}px;
                padding: 8px 16px;
                color: {COLORS["text_primary"]};
            }}
            QPushButton:hover {{
                background-color: {COLORS["bg_elevated"]};
            }}
        """)
        self.browse_btn.clicked.connect(self.on_browse)
        dir_row.addWidget(self.browse_btn)
        storage_layout.addLayout(dir_row)

        layout.addWidget(storage_section)

        # ===== Category Management Section =====
        category_section = QWidget()
        category_section.setStyleSheet(f"""
            background-color: {COLORS["bg_secondary"]};
            border-radius: {RADIUS["lg"]}px;
            padding: {SPACING["md"]}px;
        """)
        category_layout = QVBoxLayout(category_section)
        category_layout.setContentsMargins(SPACING["md"], SPACING["md"], SPACING["md"], SPACING["md"])
        category_layout.setSpacing(SPACING["md"])

        category_title = QLabel("📚 类别管理")
        category_title.setStyleSheet(f"""
            color: {COLORS["text_primary"]};
            font-size: {FONT_SIZES["md"]}px;
            font-weight: bold;
        """)
        category_layout.addWidget(category_title)

        self.category_list = QListWidget()
        self.category_list.addItems(self.config.categories)
        self.category_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLORS["bg_primary"]};
                border: 1px solid {COLORS["border"]};
                border-radius: {RADIUS["md"]}px;
                padding: {SPACING["xs"]}px;
                color: {COLORS["text_primary"]};
                min-height: 120px;
            }}
            QListWidget::item {{
                padding: {SPACING["sm"]}px;
                border-radius: {RADIUS["sm"]}px;
                color: {COLORS["text_secondary"]};
            }}
            QListWidget::item:hover {{
                background-color: {COLORS["bg_tertiary"]};
                color: {COLORS["text_primary"]};
            }}
            QListWidget::item:selected {{
                background-color: {COLORS["accent"]};
                color: white;
            }}
        """)
        category_layout.addWidget(self.category_list)

        category_btn_layout = QHBoxLayout()

        # Add category input
        self.new_category_input = QLineEdit()
        self.new_category_input.setPlaceholderText("新类别名称...")
        self.new_category_input.returnPressed.connect(self.on_add_category)
        category_btn_layout.addWidget(self.new_category_input, 1)

        self.add_cat_btn = QPushButton("+ 添加")
        self.add_cat_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["accent"]};
                border: none;
                border-radius: {RADIUS["md"]}px;
                padding: 8px 16px;
                color: white;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS["accent_hover"]};
            }}
        """)
        self.add_cat_btn.clicked.connect(self.on_add_category)
        category_btn_layout.addWidget(self.add_cat_btn)

        self.remove_cat_btn = QPushButton("🗑 删除")
        self.remove_cat_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["bg_tertiary"]};
                border: 1px solid {COLORS["border"]};
                border-radius: {RADIUS["md"]}px;
                padding: 8px 16px;
                color: {COLORS["text_secondary"]};
            }}
            QPushButton:hover {{
                background-color: {COLORS["error"]};
                color: white;
            }}
        """)
        self.remove_cat_btn.clicked.connect(self.on_remove_category)
        category_btn_layout.addWidget(self.remove_cat_btn)

        category_layout.addLayout(category_btn_layout)
        layout.addWidget(category_section)

        # Spacer
        layout.addStretch()

        # ===== Dialog Buttons =====
        button_layout = QHBoxLayout()

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["bg_tertiary"]};
                border: 1px solid {COLORS["border"]};
                border-radius: {RADIUS["md"]}px;
                padding: 12px 24px;
                color: {COLORS["text_primary"]};
            }}
            QPushButton:hover {{
                background-color: {COLORS["bg_elevated"]};
            }}
        """)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("✓ 保存")
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["accent"]};
                border: none;
                border-radius: {RADIUS["md"]}px;
                padding: 12px 24px;
                color: white;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS["accent_hover"]};
            }}
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

    def on_add_category(self):
        """Add a new category"""
        new_category = self.new_category_input.text().strip()
        if new_category:
            # Check if already exists
            existing = [self.category_list.item(i).text() for i in range(self.category_list.count())]
            if new_category not in existing:
                self.category_list.addItem(new_category)
                self.new_category_input.clear()

    def on_remove_category(self):
        """Remove selected category"""
        current_row = self.category_list.currentRow()
        if current_row >= 0:
            self.category_list.takeItem(current_row)

    def on_save(self):
        """Save settings and close"""
        # Update root dir
        new_root_dir = self.root_dir_input.text().strip()
        self.config_manager.set_root_dir(new_root_dir)

        # Get all categories from list
        categories = []
        for i in range(self.category_list.count()):
            cat = self.category_list.item(i).text().strip()
            if cat and cat not in categories:
                categories.append(cat)

        # Rebuild categories
        config = self.config_manager.load()
        for cat in config.categories:
            self.config_manager.remove_category(cat)
        for cat in categories:
            self.config_manager.add_category(cat)

        self.accept()
