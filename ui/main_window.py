"""Main window for novel downloader - Modern Dark Theme"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QComboBox, QLabel,
    QScrollArea, QGridLayout, QMessageBox, QSizePolicy, QSpacerItem, QStatusBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from typing import List

from core.plugin_registry import PluginRegistry
from core.config import ConfigManager
from core.download_manager import DownloadManager
from ui.card_widget import CardWidget
from ui.download_dialog import DownloadDialog
from ui.settings_dialog import SettingsDialog
from ui.theme import get_stylesheet, COLORS, SPACING, RADIUS, FONT_SIZES
from core.plugin_interface import SearchResult


class MainWindow(QMainWindow):
    """Main application window with modern dark UI"""

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager("config.json")
        self.config = self.config_manager.load()
        self.download_manager = DownloadManager(self.config.root_dir)
        self.plugin_registry = None

        self.init_ui()
        self.apply_theme()
        self.load_plugins()

    def apply_theme(self):
        """Apply dark theme stylesheet"""
        self.setStyleSheet(get_stylesheet())

    def init_ui(self):
        """Initialize the UI components"""
        self.setWindowTitle("小说下载器")
        self.setMinimumSize(900, 650)
        self.setFont(QFont("Segoe UI", FONT_SIZES["md"]))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])

        # ===== Header Section =====
        header_layout = QHBoxLayout()

        # Title
        title = QLabel("📚 小说下载器")
        title.setStyleSheet(f"""
            color: {COLORS["text_primary"]};
            font-size: {FONT_SIZES["2xl"]}px;
            font-weight: bold;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()

        # Settings button
        self.settings_btn = QPushButton("⚙ 设置")
        self.settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["bg_secondary"]};
                border: 1px solid {COLORS["border"]};
                border-radius: {RADIUS["md"]}px;
                padding: 8px 16px;
                color: {COLORS["text_secondary"]};
            }}
            QPushButton:hover {{
                background-color: {COLORS["bg_tertiary"]};
                color: {COLORS["text_primary"]};
            }}
        """)
        header_layout.addWidget(self.settings_btn)

        # Refresh button
        self.refresh_btn = QPushButton("🔄 刷新插件")
        self.refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["bg_secondary"]};
                border: 1px solid {COLORS["border"]};
                border-radius: {RADIUS["md"]}px;
                padding: 8px 16px;
                color: {COLORS["text_secondary"]};
            }}
            QPushButton:hover {{
                background-color: {COLORS["bg_tertiary"]};
                color: {COLORS["text_primary"]};
            }}
        """)
        header_layout.addWidget(self.refresh_btn)

        layout.addLayout(header_layout)

        # ===== Storage Info =====
        storage_layout = QHBoxLayout()
        storage_icon = QLabel("📁")
        storage_layout.addWidget(storage_icon)
        storage_layout.addWidget(QLabel("存储目录:"))
        self.root_dir_label = QLabel(self.config.root_dir if self.config.root_dir else "未设置")
        self.root_dir_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        storage_layout.addWidget(self.root_dir_label)
        storage_layout.addStretch()
        layout.addLayout(storage_layout)

        # ===== Search Section =====
        search_container = QWidget()
        search_container.setStyleSheet(f"""
            background-color: {COLORS["bg_secondary"]};
            border-radius: {RADIUS["lg"]}px;
            padding: {SPACING["md"]}px;
        """)
        search_layout = QVBoxLayout(search_container)
        search_layout.setContentsMargins(SPACING["md"], SPACING["md"], SPACING["md"], SPACING["md"])
        search_layout.setSpacing(SPACING["md"])

        # Category row
        category_row = QHBoxLayout()
        category_row.addWidget(QLabel("类别"))
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.setMinimumWidth(150)
        category_row.addWidget(self.category_combo)
        self.add_category_btn = QPushButton("+ 新增")
        self.add_category_btn.setStyleSheet(f"""
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
        category_row.addWidget(self.add_category_btn)
        category_row.addStretch()
        search_layout.addLayout(category_row)

        # Search row
        search_row = QHBoxLayout()
        self.bookname_input = QLineEdit()
        self.bookname_input.setPlaceholderText("输入书名搜索...")
        self.bookname_input.setMinimumWidth(300)
        search_row.addWidget(self.bookname_input)
        self.search_btn = QPushButton("🔍 搜索")
        self.search_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["accent"]};
                border: none;
                border-radius: {RADIUS["md"]}px;
                padding: 10px 24px;
                color: white;
                font-weight: bold;
                font-size: {FONT_SIZES["md"]}px;
            }}
            QPushButton:hover {{
                background-color: {COLORS["accent_hover"]};
            }}
            QPushButton:disabled {{
                background-color: {COLORS["bg_tertiary"]};
                color: {COLORS["text_tertiary"]};
            }}
        """)
        search_row.addWidget(self.search_btn)
        search_layout.addLayout(search_row)

        layout.addWidget(search_container)

        # ===== Results Section =====
        results_label = QLabel("搜索结果")
        results_label.setStyleSheet(f"""
            color: {COLORS["text_secondary"]};
            font-size: {FONT_SIZES["sm"]}px;
            font-weight: bold;
        """)
        layout.addWidget(results_label)

        # Results scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
        """)
        self.results_widget = QWidget()
        self.results_widget.setStyleSheet("background-color: transparent;")
        self.results_layout = QGridLayout(self.results_widget)
        self.results_layout.setContentsMargins(0, SPACING["sm"], 0, SPACING["sm"])
        self.results_layout.setSpacing(SPACING["md"])
        self.scroll_area.setWidget(self.results_widget)
        layout.addWidget(self.scroll_area, 1)

        # ===== Status Bar =====
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet(f"""
            color: {COLORS["text_tertiary"]};
            font-size: {FONT_SIZES["sm"]}px;
        """)
        self.status_bar.addPermanentWidget(self.status_label)

        # Connect signals
        self.settings_btn.clicked.connect(self.open_settings)
        self.refresh_btn.clicked.connect(self.load_plugins)
        self.search_btn.clicked.connect(self.on_search)
        self.add_category_btn.clicked.connect(self.add_category)
        self.bookname_input.returnPressed.connect(self.on_search)

        # Load categories
        self.update_category_combo()

    def load_plugins(self):
        """Load and register plugins"""
        self.plugin_registry = PluginRegistry.get_instance()
        try:
            import importlib
            from pathlib import Path

            plugins_dir = Path(__file__).parent.parent / "plugins"
            for plugin_file in plugins_dir.glob("plugin_*.py"):
                if plugin_file.stem == "base_plugin":
                    continue
                module_name = f"plugins.{plugin_file.stem}"
                importlib.import_module(module_name)

            plugin_names = self.plugin_registry.list_plugins()
            self.status_label.setText(f"已加载 {len(plugin_names)} 个插件: {', '.join(plugin_names)}")
        except Exception as e:
            self.status_label.setText(f"插件加载失败: {e}")

    def update_category_combo(self):
        """Update category combo box"""
        self.category_combo.clear()
        if self.config.categories:
            self.category_combo.addItems(self.config.categories)
        elif self.config.last_category:
            self.category_combo.addItem(self.config.last_category)

    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self.config_manager, self)
        if dialog.exec():
            self.config = self.config_manager.load()
            self.download_manager = DownloadManager(self.config.root_dir)
            self.root_dir_label.setText(self.config.root_dir if self.config.root_dir else "未设置")
            self.update_category_combo()

    def add_category(self):
        """Add a new category"""
        new_category = self.category_combo.currentText().strip()
        if new_category:
            self.config_manager.add_category(new_category)
            self.config = self.config_manager.load()
            self.update_category_combo()
            self.status_label.setText(f"已添加类别: {new_category}")

    def on_search(self):
        """Handle search button click"""
        keyword = self.bookname_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, "提示", "请输入书名关键字")
            return

        if not self.config.root_dir:
            QMessageBox.warning(self, "设置", "请先在设置中设置存储目录")
            return

        self.status_label.setText(f"搜索中: {keyword}...")
        self.search_btn.setEnabled(False)
        self.bookname_input.setEnabled(False)

        try:
            all_results = []
            for plugin_name in self.plugin_registry.list_plugins():
                plugin = self.plugin_registry.get_plugin(plugin_name)
                if plugin:
                    try:
                        results = plugin.search(keyword)
                        all_results.extend(results)
                    except Exception as e:
                        pass

            self.display_results(all_results)
            self.status_label.setText(f"找到 {len(all_results)} 个结果")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"搜索失败: {e}")
            self.status_label.setText("搜索失败")
        finally:
            self.search_btn.setEnabled(True)
            self.bookname_input.setEnabled(True)

    def display_results(self, results: List[SearchResult]):
        """Display search results as cards"""
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not results:
            empty_widget = QLabel("暂无结果，请尝试其他关键词")
            empty_widget.setStyleSheet(f"""
                color: {COLORS["text_tertiary"]};
                font-size: {FONT_SIZES["md"]}px;
                padding: 40px;
            """)
            empty_widget.setAlignment(Qt.AlignCenter)
            self.results_layout.addWidget(empty_widget, 0, 0)
            return

        for i, result in enumerate(results):
            row = i // 4
            col = i % 4
            card = CardWidget(result)
            card.double_clicked.connect(self.on_card_double_clicked)
            self.results_layout.addWidget(card, row, col)

    def on_card_double_clicked(self, result: SearchResult):
        """Handle card double click - start download"""
        category = self.category_combo.currentText().strip()
        if not category:
            QMessageBox.warning(self, "提示", "请选择或输入类别")
            return

        book_save_path = self.download_manager.get_book_save_path(
            self.config.root_dir, category, result.title
        )

        dialog = DownloadDialog(
            result=result,
            book_save_path=book_save_path,
            download_manager=self.download_manager,
            parent=self
        )
        dialog.exec()
