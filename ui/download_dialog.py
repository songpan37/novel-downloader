"""Download dialog for showing download progress - Modern Dark Theme"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QListWidget, QPushButton, QWidget,
    QComboBox, QMessageBox
)
from PySide6.QtCore import QThread, Signal, Qt
from typing import List, Dict
import os
import re

from core.plugin_interface import SearchResult, ChapterInfo
from core.download_manager import DownloadManager, DownloadMeta
from core.config import ConfigManager
from ui.theme import get_stylesheet, COLORS, SPACING, RADIUS, FONT_SIZES
from datetime import datetime


class DownloadWorker(QThread):
    """Worker thread for downloading chapters"""

    MAX_RETRIES = 3
    RETRY_DELAY = 2

    progress = Signal(int, int)
    chapter_status = Signal(int, str, str)  # index, status, title
    finished = Signal()
    error = Signal(str)

    def __init__(self, result: SearchResult, book_save_path: str,
                 download_manager: DownloadManager, plugin, parent=None):
        super().__init__(parent)
        self.result = result
        self.book_save_path = book_save_path
        self.download_manager = download_manager
        self.plugin = plugin  # 独立的插件实例
        self._is_running = True

    def _log(self, msg: str):
        """Print log message with timestamp."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [下载] {msg}")

    def run(self):
        """Execute download"""
        self._log(f"开始下载: 《{self.result.title}》")
        self._log(f"保存路径: {self.book_save_path}")
        self._log(f"来源插件: {self.result.plugin}")

        try:
            if not self.plugin:
                error_msg = f"找不到插件: {self.result.plugin}"
                self._log(f"错误: {error_msg}")
                self.error.emit(error_msg)
                return

            self._log("正在获取章节列表...")
            self.chapter_status.emit(-1, "获取章节列表...", "")
            chapters = self.plugin.get_chapter_list(self.result.url)

            if not chapters:
                error_msg = "无法获取章节列表"
                self._log(f"错误: {error_msg}")
                self.error.emit(error_msg)
                return

            total = len(chapters)
            self._log(f"共 {total} 个章节，开始下载...")
            self._log(f"URL: {self.result.url}")

            os.makedirs(self.book_save_path, exist_ok=True)

            existing_meta = self.download_manager.load_meta(self.result.url, self.result.plugin)
            downloaded = {}
            if existing_meta:
                downloaded = existing_meta.downloaded_chapters
                self._log(f"发现已下载章节: {len(downloaded)} 个，将跳过")

            meta = DownloadMeta(
                book_url=self.result.url,
                plugin=self.result.plugin,
                downloaded_chapters=downloaded,
                total_chapters=total,
                last_updated=datetime.now().isoformat()
            )

            for i, chapter in enumerate(chapters):
                if not self._is_running:
                    self._log("下载已取消")
                    break

                chapter_key = str(chapter.index)

                # Check if chapter file already exists using find_chapter_file_path
                existing_file = self.download_manager.find_chapter_file_path(
                    self.book_save_path, chapter.index
                )
                file_exists_and_not_empty = existing_file and os.path.getsize(existing_file) > 0

                if chapter_key in downloaded or file_exists_and_not_empty:
                    if file_exists_and_not_empty and chapter_key not in downloaded:
                        # File exists but not in meta, add to downloaded
                        downloaded[chapter_key] = chapter.title
                        meta.downloaded_chapters = downloaded
                        self.download_manager.save_meta(self.book_save_path, meta)
                    self._log(f"[{i+1}/{total}] 跳过 第{chapter.index}章 - {chapter.title} (已存在)")
                    self.chapter_status.emit(chapter.index, "已存在", chapter.title)
                    continue

                self._log(f"[{i+1}/{total}] 下载 第{chapter.index}章 - {chapter.title}")
                self._log(f"  URL: {chapter.url}")
                self.chapter_status.emit(chapter.index, "下载中...", chapter.title)

                # Retry loop for chapter download
                content = None
                chaptername = ""
                last_error = None
                for retry in range(self.MAX_RETRIES):
                    try:
                        result = self.plugin.get_chapter_content(chapter.url)
                        # Handle both tuple (bqg) and string (other plugins) returns
                        if isinstance(result, tuple):
                            chaptername, content = result
                            if chaptername:
                                chapter.title = chaptername
                        else:
                            content = result

                        if content:
                            break  # Success, exit retry loop
                        else:
                            last_error = "内容为空"
                    except Exception as e:
                        last_error = str(e)

                    if retry < self.MAX_RETRIES - 1:
                        self._log(f"  下载失败，{self.RETRY_DELAY}秒后重试... ({retry + 1}/{self.MAX_RETRIES})")
                        self.chapter_status.emit(chapter.index, f"重试中({retry + 1}/{self.MAX_RETRIES})...", chapter.title)
                        from time import sleep
                        sleep(self.RETRY_DELAY)

                if content:
                    self.download_manager.save_chapter_content(
                        self.book_save_path,
                        chapter.index,
                        chapter.title,
                        content
                    )
                    downloaded[chapter_key] = chapter.title
                    meta.downloaded_chapters = downloaded
                    meta.last_updated = datetime.now().isoformat()
                    self.download_manager.save_meta(self.book_save_path, meta)
                    self._log(f"  完成，内容长度: {len(content)} 字符")
                    self.chapter_status.emit(chapter.index, "完成", chapter.title)
                    self.progress.emit(i + 1, total)
                else:
                    self._log(f"  失败: {last_error or '未知错误'}")
                    self.chapter_status.emit(chapter.index, f"失败 - {chapter.title}", chapter.title)

            if len(downloaded) == total:
                self.download_manager.delete_meta(self.book_save_path)

            self._log(f"下载完成! 共 {len(downloaded)}/{total} 个章节")
            self.finished.emit()

        except Exception as e:
            error_msg = str(e)
            self._log(f"下载出错: {error_msg}")
            import traceback
            traceback.print_exc()
            self.error.emit(error_msg)

    def stop(self):
        """Stop the download"""
        self._is_running = False


class DownloadDialog(QDialog):
    """Download dialog with category selection and download progress"""

    def __init__(self, result: SearchResult, download_manager: DownloadManager,
                 config_manager: ConfigManager, plugin, parent=None):
        super().__init__(parent)
        self.result = result
        self.download_manager = download_manager
        self.config_manager = config_manager
        self.plugin = plugin  # 独立的插件实例
        self.config = config_manager.load()
        self.worker = None
        self.chapter_status_map = {}
        self.chapter_titles_map = {}  # Map chapter index to title
        self.book_save_path = ""
        self.category_selected = None
        self.init_ui()

    def init_ui(self):
        """Initialize the dialog UI"""
        self.setWindowTitle("下载小说")
        self.setMinimumSize(520, 350)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
            QWidget {
                background-color: #1a1a1a;
                color: #e0e0e0;
            }
            QLabel {
                color: #a0a0a0;
            }
            QComboBox {
                background-color: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px 12px;
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
                padding: 8px 16px;
                color: #e0e0e0;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QListWidget {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                color: #e0e0e0;
            }
            QListWidget::item {
                padding: 4px 8px;
                color: #808080;
            }
            QListWidget::item:selected {
                background-color: transparent;
                color: #e0e0e0;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Book info
        info_label = QLabel(f"《{self.result.title}》")
        info_label.setStyleSheet("color: #e0e0e0; font-size: 16px; font-weight: bold;")
        layout.addWidget(info_label)

        author_label = QLabel(f"作者: {self.result.author}  来源: {self.result.plugin}")
        author_label.setStyleSheet("color: #808080; font-size: 13px;")
        layout.addWidget(author_label)

        # Category selection section
        category_label = QLabel("选择保存类别")
        category_label.setStyleSheet("color: #808080; font-size: 13px;")
        layout.addWidget(category_label)

        category_layout = QHBoxLayout()
        category_layout.setSpacing(8)

        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(200)
        self.update_category_combo()
        category_layout.addWidget(self.category_combo)

        self.add_category_btn = QPushButton("新增类别")
        self.add_category_btn.setFixedWidth(80)
        self.add_category_btn.clicked.connect(self.add_category)
        category_layout.addWidget(self.add_category_btn)

        self.delete_category_btn = QPushButton("删除类别")
        self.delete_category_btn.setFixedWidth(80)
        self.delete_category_btn.clicked.connect(self.delete_category)
        category_layout.addWidget(self.delete_category_btn)

        category_layout.addStretch()
        layout.addLayout(category_layout)

        # Download path preview
        self.path_label = QLabel("保存路径: ")
        self.path_label.setStyleSheet("color: #606060; font-size: 12px;")
        self.path_label.setWordWrap(True)
        layout.addWidget(self.path_label)

        self.category_combo.currentTextChanged.connect(self.on_category_changed)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.on_cancel)
        button_layout.addWidget(self.cancel_btn)

        self.confirm_btn = QPushButton("开始下载")
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a7c4a;
                border: none;
                color: white;
            }
            QPushButton:hover {
                background-color: #5a9c5a;
            }
        """)
        self.confirm_btn.clicked.connect(self.on_confirm)
        button_layout.addWidget(self.confirm_btn)

        self.open_folder_btn = QPushButton("查看下载")
        self.open_folder_btn.setFixedWidth(80)
        self.open_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a7c4a;
                border: none;
                color: white;
            }
            QPushButton:hover {
                background-color: #5a9c5a;
            }
        """)
        self.open_folder_btn.clicked.connect(self.on_open_folder)
        self.open_folder_btn.setVisible(False)
        button_layout.addWidget(self.open_folder_btn)

        self.merge_btn = QPushButton("合并章节")
        self.merge_btn.setFixedWidth(60)
        self.merge_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a7c4a;
                border: none;
                color: white;
            }
            QPushButton:hover {
                background-color: #5a9c5a;
            }
        """)
        self.merge_btn.clicked.connect(self.on_merge)
        self.merge_btn.setVisible(False)
        button_layout.addWidget(self.merge_btn)

        layout.addLayout(button_layout)

        # Download progress section (hidden initially)
        self.progress_widget = QWidget()
        self.progress_layout = QVBoxLayout(self.progress_widget)
        self.progress_layout.setContentsMargins(0, 16, 0, 0)
        self.progress_layout.setSpacing(12)

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #2a2a2a;
                border: none;
                border-radius: 4px;
                height: 8px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4a7c4a;
                border-radius: 4px;
            }
        """)
        self.progress_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("准备下载...")
        self.status_label.setStyleSheet("color: #808080; font-size: 13px;")
        self.progress_layout.addWidget(self.status_label)

        self.chapter_list = QListWidget()
        self.chapter_list.setMaximumHeight(150)
        self.progress_layout.addWidget(self.chapter_list)

        layout.addWidget(self.progress_widget)
        self.progress_widget.setVisible(False)

    def update_category_combo(self):
        """Update category combo box."""
        self.category_combo.blockSignals(True)
        self.category_combo.clear()

        self.category_combo.addItem("请选择类别", userData="")
        self.category_combo.setCurrentIndex(0)

        # Add all saved categories
        for cat in self.config.categories:
            self.category_combo.addItem(cat, userData=cat)

        self.category_combo.blockSignals(False)

    def on_category_changed(self, text: str):
        """Handle category selection changed."""
        if text == "请选择类别" or not text:
            self.path_label.setText("保存路径: ")
            self.book_save_path = ""
            return

        self.book_save_path = self.download_manager.get_book_save_path(
            self.config.root_dir, text, self.result.title
        )
        self.path_label.setText(f"保存路径: {self.book_save_path}")
        self.config_manager.set_last_category(text)

    def add_category(self):
        """Show dialog to add a new category."""
        from PySide6.QtWidgets import QInputDialog

        new_category, ok = QInputDialog.getText(
            self, "新增类别", "请输入新类别名称:", flags=Qt.WindowType.Dialog
        )

        if ok and new_category.strip():
            new_category = new_category.strip()
            self.config_manager.add_category(new_category)
            self.config = self.config_manager.load()
            self.update_category_combo()
            index = self.category_combo.findText(new_category)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)

    def delete_category(self):
        """Delete the currently selected category."""
        current = self.category_combo.currentText()
        if current == "请选择类别" or not current:
            QMessageBox.warning(self, "提示", "请先选择一个类别")
            return

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除类别 '{current}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.config_manager.remove_category(current)
            self.config = self.config_manager.load()
            self.update_category_combo()

    def on_confirm(self):
        """Handle confirm button - start download."""
        category = self.category_combo.currentText()
        if category == "请选择类别" or not category:
            QMessageBox.warning(self, "提示", "请先选择一个类别")
            return

        if not self.config.root_dir:
            QMessageBox.warning(self, "提示", "请先在设置中设置存储目录")
            return

        self.category_selected = category
        self.book_save_path = self.download_manager.get_book_save_path(
            self.config.root_dir, category, self.result.title
        )

        # Reset chapter status maps for new download
        self.chapter_status_map = {}
        self.chapter_titles_map = {}
        self.chapter_list.clear()

        # Hide category selection, show progress
        self.progress_widget.setVisible(True)
        self.setMinimumSize(520, 500)

        # Disable confirm button and category controls
        self.confirm_btn.setEnabled(False)
        self.category_combo.setEnabled(False)
        self.add_category_btn.setEnabled(False)
        self.delete_category_btn.setEnabled(False)
        # Show open folder and merge buttons
        self.open_folder_btn.setVisible(True)
        self.merge_btn.setVisible(True)

        # Start download
        self.start_download()

    def start_download(self):
        """Start the download worker."""
        self.worker = DownloadWorker(
            self.result,
            self.book_save_path,
            self.download_manager,
            self.plugin,  # 传入独立的插件实例
            self
        )
        self.worker.progress.connect(self.on_progress)
        self.worker.chapter_status.connect(self.on_chapter_status)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_progress(self, current: int, total: int):
        """Handle progress update."""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        percentage = int(current / total * 100) if total > 0 else 0
        self.status_label.setText(f"进度: {current}/{total} ({percentage}%)")

    def on_chapter_status(self, index: int, status: str, title: str = ""):
        """Handle chapter status update."""
        if index == -1:
            self.status_label.setText(status)
            return

        # Store title for use in merge
        if title:
            self.chapter_titles_map[index] = title

        # Get the expected filename - use title directly if provided, otherwise construct
        if title:
            # Remove duplicate "第x章 " prefix if present (but keep chapter number in filename)
            match = re.match(r'^第(\d+)章\s+(.*)', title)
            if match:
                safe_title = match.group(2).strip()
            else:
                safe_title = title
            # Sanitize filename
            illegal_chars = '\\/:*?"<>|'
            for char in illegal_chars:
                safe_title = safe_title.replace(char, '_')
            filename = f"第{index}章 {safe_title}.txt" if safe_title else f"第{index}章.txt"
        else:
            filename = f"第{index}章.txt"

        item_text = f"{filename} - {status}"

        if index not in self.chapter_status_map:
            self.chapter_list.addItem(item_text)
            self.chapter_status_map[index] = self.chapter_list.count() - 1
        else:
            item = self.chapter_list.item(self.chapter_status_map[index])
            item.setText(item_text)

        self.chapter_list.scrollToItem(self.chapter_list.item(self.chapter_status_map[index]))

    def on_finished(self):
        """Handle download completion."""
        self.status_label.setText("下载完成!")
        self.status_label.setStyleSheet("color: #4a9f4a; font-size: 13px;")
        self.cancel_btn.setText("关闭")

    def on_error(self, error_msg: str):
        """Handle download error."""
        QMessageBox.critical(self, "错误", f"下载失败: {error_msg}")

    def on_open_folder(self):
        """Open the download folder in file explorer."""
        if self.book_save_path and os.path.exists(self.book_save_path):
            from PySide6.QtGui import QDesktopServices
            from PySide6.QtCore import QUrl
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.book_save_path))

    def on_merge(self):
        """Merge downloaded chapters into a single file."""
        if not self.book_save_path or not os.path.exists(self.book_save_path):
            QMessageBox.warning(self, "提示", "下载目录不存在")
            return

        # Get all chapter files and sort by chapter number
        chapter_files = []
        for filename in os.listdir(self.book_save_path):
            if filename.endswith('.txt'):
                # Extract chapter number from filename like "第1章 xxx.txt"
                match = re.match(r'^第(\d+)章\s+', filename)
                if match:
                    chapter_num = int(match.group(1))
                    chapter_files.append((chapter_num, filename))

        if not chapter_files:
            QMessageBox.warning(self, "提示", "没有找到已下载的章节文件")
            return

        # Sort by chapter number
        chapter_files.sort(key=lambda x: x[0])

        # Merge content
        merged_content = []
        for chapter_num, filename in chapter_files:
            filepath = os.path.join(self.book_save_path, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                merged_content.append(f"第{chapter_num}章\n{content}\n\n")

        # Save merged file
        book_title = self.result.title
        merged_filename = f"{book_title}.txt"
        merged_filepath = os.path.join(self.book_save_path, merged_filename)

        with open(merged_filepath, 'w', encoding='utf-8') as f:
            f.writelines(merged_content)

        QMessageBox.information(self, "完成", f"已合并 {len(chapter_files)} 个章节\n保存至: {merged_filename}")

    def on_cancel(self):
        """Handle cancel button."""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        self.reject()