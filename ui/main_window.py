"""Main window for novel downloader - Simple Clean Style"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QAbstractItemView,
    QMessageBox, QSizePolicy, QStatusBar, QListView, QTabWidget
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.plugin_registry import PluginRegistry
from core.config import ConfigManager
from core.download_manager import DownloadManager
from ui.download_dialog import DownloadDialog
from ui.settings_dialog import SettingsDialog
from core.plugin_interface import SearchResult

# Import plugin factory functions
import plugins.plugin_3yt as plugin_3yt_module
import plugins.plugin_92yq as plugin_92yq_module
import plugins.plugin_bqg as plugin_bqg_module


class SearchWorker(QThread):
    """Worker thread for searching a single plugin."""

    # Signals for search results
    result_ready = Signal(str, list)  # plugin_name, results
    search_failed = Signal(str, str)  # plugin_name, error_message
    search_finished = Signal(str)  # plugin_name

    def __init__(self, plugin_name: str, plugin, keyword: str, parent=None):
        super().__init__(parent)
        self.plugin_name = plugin_name
        self.plugin = plugin
        self.keyword = keyword

    def run(self):
        """Execute the search."""
        try:
            results = self.plugin.search(self.keyword)
            self.result_ready.emit(self.plugin_name, results)
        except Exception as e:
            self.search_failed.emit(self.plugin_name, str(e))
        finally:
            self.search_finished.emit(self.plugin_name)


class MainWindow(QMainWindow):
    """Main application window with simple clean UI"""

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager("config.json")
        self.config = self.config_manager.load()
        self.download_manager = DownloadManager(self.config.root_dir)
        self.plugin_registry = None

        # Store search results by plugin for tab display
        self._search_results_by_plugin: Dict[str, List[SearchResult]] = {}
        self._search_keyword: str = ""

        # Track active search workers for cleanup
        self._search_workers: Dict[str, SearchWorker] = {}
        self._active_plugin_count = 0
        self._finished_plugin_count = 0

        self.init_ui()
        self.load_plugins()

    def init_ui(self):
        """Initialize the UI components"""
        self.setWindowTitle("小说下载器")
        self.setMinimumSize(800, 600)
        self.setFont(QFont("Segoe UI", 10))

        # Set dark background
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
            QWidget {
                background-color: #1a1a1a;
                color: #e0e0e0;
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
            QComboBox {
                background-color: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px 10px;
                color: #e0e0e0;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QComboBox QAbstractItemView {
                background-color: #2a2a2a;
                border: 1px solid #404040;
                selection-background-color: #3a3a3a;
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
            QLabel {
                color: #a0a0a0;
            }
            QStatusBar {
                background-color: #1a1a1a;
                color: #606060;
            }
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 10px;
            }
            QScrollBar::handle {
                background-color: #404040;
                border-radius: 5px;
            }
            QScrollBar::handle:hover {
                background-color: #505050;
            }
            QTabWidget::pane {
                background-color: transparent;
                border: none;
            }
            QToolTip {
                color: #000000;
                background-color: #f0f0f0;
                border: 1px solid #ccc;
            }
            QTabBar::tab {
                background-color: #2a2a2a;
                color: #808080;
                padding: 8px 16px;
                border: 1px solid #3a3a3a;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #3a3a3a;
                color: #e0e0e0;
            }
            QTabBar::tab:hover:selected {
                background-color: #3a3a3a;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # ===== Header =====
        header_layout = QHBoxLayout()

        title = QLabel("小说下载器")
        title.setStyleSheet("color: #e0e0e0; font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        settings_btn = QPushButton("设置")
        settings_btn.clicked.connect(self.open_settings)
        header_layout.addWidget(settings_btn)

        layout.addLayout(header_layout)

        # ===== Storage Info =====
        storage_layout = QHBoxLayout()
        storage_layout.addWidget(QLabel("存储目录:"))
        self.root_dir_label = QLabel(self.config.root_dir if self.config.root_dir else "未设置")
        self.root_dir_label.setStyleSheet("color: #606060;")
        storage_layout.addWidget(self.root_dir_label)
        storage_layout.addStretch()
        layout.addLayout(storage_layout)

        # ===== Search Section =====
        search_row_layout = QHBoxLayout()
        search_row_layout.setSpacing(12)

        self.bookname_input = QLineEdit()
        self.bookname_input.setPlaceholderText("输入书名搜索...")
        self.bookname_input.setMinimumWidth(300)
        self.bookname_input.returnPressed.connect(self.on_search)
        search_row_layout.addWidget(self.bookname_input, 1)

        self.search_btn = QPushButton("搜索")
        self.search_btn.setFixedWidth(80)
        self.search_btn.clicked.connect(self.on_search)
        search_row_layout.addWidget(self.search_btn)

        layout.addLayout(search_row_layout)

        # ===== Results Section =====
        results_label = QLabel("搜索结果")
        results_label.setStyleSheet("color: #808080; font-size: 13px; font-weight: bold;")
        layout.addWidget(results_label)

        # Tab widget for results
        self.results_tabs = QTabWidget()
        self.results_tabs.setStyleSheet("""
            QTabWidget {
                background-color: transparent;
            }
            QTabWidget::pane {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
            }
        """)

        # Tab 1: Exact match results
        self.exact_list = QListWidget()
        self.exact_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                background-color: transparent;
                border-bottom: 1px solid #3a3a3a;
                padding: 4px 0;
            }
            QListWidget::item:selected {
                background-color: transparent;
            }
        """)
        self.exact_list.itemDoubleClicked.connect(self.on_result_double_clicked)
        self.results_tabs.addTab(self.exact_list, "精确匹配")

        # Tab 2: Other results (grouped by plugin)
        self.other_tabs = QTabWidget()
        self.other_tabs.setDocumentMode(True)
        self.results_tabs.addTab(self.other_tabs, "其他结果")

        layout.addWidget(self.results_tabs, 1)

        # ===== Status Bar =====
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("就绪")
        self.status_bar.addPermanentWidget(self.status_label)

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

    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self.config_manager, self)
        if dialog.exec():
            self.config = self.config_manager.load()
            self.download_manager = DownloadManager(self.config.root_dir)
            self.root_dir_label.setText(self.config.root_dir if self.config.root_dir else "未设置")

    def on_search(self):
        """Handle search button click - starts async search for each plugin."""
        keyword = self.bookname_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, "提示", "请输入书名关键字")
            return

        if not self.config.root_dir:
            QMessageBox.warning(self, "设置", "请先在设置中设置存储目录")
            return

        self._search_keyword = keyword
        self.status_label.setText(f"搜索中: {keyword}...")
        self.search_btn.setEnabled(False)
        self.bookname_input.setEnabled(False)

        # Clear previous results
        self.exact_list.clear()
        self.other_tabs.clear()
        self._search_results_by_plugin.clear()
        self._finished_plugin_count = 0

        # Start async search for each plugin
        plugin_names = self.plugin_registry.list_plugins()
        self._active_plugin_count = len(plugin_names)

        for plugin_name in plugin_names:
            plugin = self.plugin_registry.get_plugin(plugin_name)
            if not plugin:
                self._on_plugin_search_finished(plugin_name)
                continue

            worker = SearchWorker(plugin_name, plugin, keyword, self)
            worker.result_ready.connect(self._on_search_result_ready)
            worker.search_failed.connect(self._on_search_failed)
            worker.search_finished.connect(self._on_plugin_search_finished)
            worker.start()

            self._search_workers[plugin_name] = worker

    def _on_search_result_ready(self, plugin_name: str, results: List[SearchResult]):
        """Handle results from a single plugin - append to display."""
        if plugin_name not in self._search_results_by_plugin:
            self._search_results_by_plugin[plugin_name] = results

        if results:
            self._append_plugin_results(plugin_name, results)

    def _on_search_failed(self, plugin_name: str, error_message: str):
        """Handle search failure from a plugin."""
        self.status_label.setText(f"插件 {plugin_name} 搜索失败: {error_message}")

    def _on_plugin_search_finished(self, plugin_name: str):
        """Handle when a plugin search is complete."""
        self._finished_plugin_count += 1

        # Remove worker from tracking
        if plugin_name in self._search_workers:
            del self._search_workers[plugin_name]

        # Update status
        remaining = self._active_plugin_count - self._finished_plugin_count
        self.status_label.setText(f"搜索中: {self._search_keyword}... ({remaining} 个插件剩余)")

        # Check if all plugins finished
        if self._finished_plugin_count >= self._active_plugin_count:
            total_results = sum(len(r) for r in self._search_results_by_plugin.values())
            if total_results > 0:
                self.status_label.setText(f"找到 {total_results} 个结果")
            else:
                self.status_label.setText("未找到结果，请尝试其他关键词")

            self.search_btn.setEnabled(True)
            self.bookname_input.setEnabled(True)

    def _append_plugin_results(self, plugin_name: str, results: List[SearchResult]):
        """Append a single plugin's results to the display without clearing existing results."""
        if not results:
            return

        # Normalize keyword for comparison
        normalized_keyword = self._search_keyword.replace(" ", "").lower()

        # Separate exact matches and other results for this plugin
        exact_matches = []
        other_results = []

        for result in results:
            normalized_title = result.title.replace(" ", "").lower()
            if normalized_title == normalized_keyword:
                exact_matches.append(result)
            else:
                other_results.append(result)

        # Add exact matches to the exact list
        if exact_matches:
            self._populate_list_widget(self.exact_list, exact_matches)

        # Add other results to the plugin's tab (create if doesn't exist)
        if other_results:
            # Check if this plugin already has a tab
            existing_tab_index = -1
            for i in range(self.other_tabs.count()):
                if self.other_tabs.tabText(i) == plugin_name:
                    existing_tab_index = i
                    break

            if existing_tab_index >= 0:
                # Append to existing tab
                plugin_list = self.other_tabs.widget(existing_tab_index)
                self._populate_list_widget(plugin_list, other_results)
            else:
                # Create new tab for this plugin
                plugin_list = QListWidget()
                plugin_list.setStyleSheet("""
                    QListWidget {
                        background-color: transparent;
                        border: none;
                        outline: none;
                    }
                    QListWidget::item {
                        background-color: transparent;
                        border-bottom: 1px solid #3a3a3a;
                        padding: 4px 0;
                    }
                    QListWidget::item:selected {
                        background-color: transparent;
                    }
                """)
                plugin_list.itemDoubleClicked.connect(self.on_result_double_clicked)
                self._populate_list_widget(plugin_list, other_results)
                self.other_tabs.addTab(plugin_list, plugin_name)

        # Enable the "其他结果" tab if it has content
        if self.other_tabs.count() > 0:
            self.results_tabs.setTabEnabled(1, True)

    def display_results(self, results: List[SearchResult]):
        """Display search results in tabs - exact match and other results grouped by plugin."""
        self.exact_list.clear()
        self.other_tabs.clear()

        if not results:
            return

        # Normalize keyword for comparison (remove spaces, lowercase)
        normalized_keyword = self._search_keyword.replace(" ", "").lower()

        # Separate exact matches and other results
        exact_matches = []
        other_results = []

        for result in results:
            normalized_title = result.title.replace(" ", "").lower()
            if normalized_title == normalized_keyword:
                exact_matches.append(result)
            else:
                other_results.append(result)

        # Display exact matches in first tab
        self._populate_list_widget(self.exact_list, exact_matches)

        # Display other results grouped by plugin in second tab
        if other_results:
            plugin_results: Dict[str, List[SearchResult]] = {}
            for result in other_results:
                if result.plugin not in plugin_results:
                    plugin_results[result.plugin] = []
                plugin_results[result.plugin].append(result)

            for plugin_name, plugin_results_list in plugin_results.items():
                plugin_list = QListWidget()
                plugin_list.setStyleSheet("""
                    QListWidget {
                        background-color: transparent;
                        border: none;
                        outline: none;
                    }
                    QListWidget::item {
                        background-color: transparent;
                        border-bottom: 1px solid #3a3a3a;
                        padding: 4px 0;
                    }
                    QListWidget::item:selected {
                        background-color: transparent;
                    }
                """)
                plugin_list.itemDoubleClicked.connect(self.on_result_double_clicked)
                self._populate_list_widget(plugin_list, plugin_results_list)
                self.other_tabs.addTab(plugin_list, plugin_name)

            self.results_tabs.setTabEnabled(1, True)
        else:
            self.results_tabs.setTabEnabled(1, False)

    def _populate_list_widget(self, list_widget: QListWidget, results: List[SearchResult]):
        """Populate a list widget with search results."""
        for result in results:
            item = QListWidgetItem(list_widget)
            item.setData(Qt.UserRole, result)

            # Create widget to hold content
            widget = QWidget()
            main_layout = QHBoxLayout(widget)
            main_layout.setContentsMargins(12, 12, 12, 12)
            main_layout.setSpacing(16)

            # Left side: content
            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            content_layout.setContentsMargins(0, 0, 0, 0)
            content_layout.setSpacing(6)

            # Title row
            title_layout = QHBoxLayout()
            title_layout.setSpacing(8)

            # Truncate title if longer than 15 characters
            display_title = result.title
            if len(display_title) > 15:
                display_title = display_title[:15] + "..."

            title_label = QLabel(display_title)
            title_label.setStyleSheet("color: #e0e0e0; font-size: 15px; font-weight: bold;")
            title_label.setWordWrap(False)
            title_label.setToolTip(result.title)  # Show full title on hover
            title_layout.addWidget(title_label)
            title_layout.addStretch()

            content_layout.addLayout(title_layout)

            # Info row: 作者 | 来源 | 状态
            info_layout = QHBoxLayout()
            info_layout.setSpacing(16)

            author_label = QLabel(f"作者: {result.author}")
            author_label.setStyleSheet("color: #808080; font-size: 13px;")
            info_layout.addWidget(author_label)

            source_label = QLabel(f"来源: {result.plugin}")
            source_label.setStyleSheet("color: #606060; font-size: 12px;")
            info_layout.addWidget(source_label)

            # Status
            status_text = "完结" if result.status.value == "完结" else "连载"
            status_color = "#4a9f4a" if status_text == "完结" else "#c9a227"
            status_label = QLabel(status_text)
            status_label.setStyleSheet(f"color: {status_color}; font-size: 12px;")
            info_layout.addWidget(status_label)

            info_layout.addStretch()

            content_layout.addLayout(info_layout)

            main_layout.addWidget(content_widget, 1)

            # Right side: buttons in one row
            buttons_widget = QWidget()
            buttons_layout = QHBoxLayout(buttons_widget)
            buttons_layout.setContentsMargins(0, 0, 0, 0)
            buttons_layout.setSpacing(8)
            buttons_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # Download button
            download_btn = QPushButton("下载")
            download_btn.setFixedWidth(60)
            download_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4a7c4a;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    color: white;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #5a9c5a;
                }
            """)
            download_btn.clicked.connect(lambda checked, r=result: self.on_download_clicked(r))
            buttons_layout.addWidget(download_btn)

            # Open link button
            open_btn = QPushButton("原链接")
            open_btn.setFixedWidth(60)
            open_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4a7c4a;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    color: white;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #5a9c5a;
                }
            """)
            open_btn.clicked.connect(lambda checked, url=result.url: self.open_url(url))
            buttons_layout.addWidget(open_btn)

            main_layout.addWidget(buttons_widget)

            list_widget.setItemWidget(item, widget)

            # Set a minimum height to ensure content is not truncated
            size_hint = widget.sizeHint()
            size_hint.setHeight(max(size_hint.height(), 70))
            item.setSizeHint(size_hint)

    def on_result_double_clicked(self, item: QListWidgetItem):
        """Handle result item double click."""
        result = item.data(Qt.UserRole)
        if not result:
            return

        dialog = DownloadDialog(
            result=result,
            download_manager=self.download_manager,
            config_manager=self.config_manager,
            parent=self
        )
        dialog.exec()

    def on_download_clicked(self, result: SearchResult):
        """Handle download button click - creates independent plugin instance."""
        # Create independent plugin instance for this download
        plugin = self._create_plugin_instance(result.plugin)

        dialog = DownloadDialog(
            result=result,
            download_manager=self.download_manager,
            config_manager=self.config_manager,
            plugin=plugin,  # 传入独立的插件实例
            parent=self
        )
        dialog.show()  # 非阻塞显示窗口

    def _create_plugin_instance(self, plugin_name: str):
        """Create an independent plugin instance for a download.

        Each download gets its own plugin instance to avoid conflicts.
        """
        if plugin_name == '3yt':
            return plugin_3yt_module.create_instance(headless=False, slow_mo=100)
        elif plugin_name == '92yq':
            return plugin_92yq_module.create_instance()
        elif plugin_name == 'bqg':
            return plugin_bqg_module.create_instance()
        else:
            # Fallback to registry plugin
            return self.plugin_registry.get_plugin(plugin_name)

    def open_url(self, url: str):
        """Open URL in default browser."""
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl
        QDesktopServices.openUrl(QUrl(url))

    def closeEvent(self, event):
        """Handle window close event - cleanup browser resources."""
        try:
            from plugins.plugin_3yt import close_plugin
            close_plugin()
        except Exception:
            pass
        event.accept()