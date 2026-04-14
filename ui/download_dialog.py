"""Download dialog for showing download progress - Modern Dark Theme"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QListWidget, QPushButton, QWidget
)
from PySide6.QtCore import QThread, Signal, Qt
from typing import List
import os

from core.plugin_interface import SearchResult, ChapterInfo
from core.plugin_registry import PluginRegistry
from core.download_manager import DownloadManager, DownloadMeta
from ui.theme import get_stylesheet, COLORS, SPACING, RADIUS, FONT_SIZES
from datetime import datetime


class DownloadWorker(QThread):
    """Worker thread for downloading chapters"""

    progress = Signal(int, int)
    chapter_status = Signal(int, str)
    finished = Signal()
    error = Signal(str)

    def __init__(self, result: SearchResult, book_save_path: str,
                 download_manager: DownloadManager, parent=None):
        super().__init__(parent)
        self.result = result
        self.book_save_path = book_save_path
        self.download_manager = download_manager
        self._is_running = True

    def run(self):
        """Execute download"""
        try:
            plugin = PluginRegistry.get_instance().get_plugin(self.result.plugin)
            if not plugin:
                self.error.emit(f"找不到插件: {self.result.plugin}")
                return

            self.chapter_status.emit(-1, "获取章节列表...")
            chapters = plugin.get_chapter_list(self.result.url)

            if not chapters:
                self.error.emit("无法获取章节列表")
                return

            total = len(chapters)
            os.makedirs(self.book_save_path, exist_ok=True)

            existing_meta = self.download_manager.load_meta(self.result.url, self.result.plugin)
            downloaded = {}
            if existing_meta:
                downloaded = existing_meta.downloaded_chapters

            meta = DownloadMeta(
                book_url=self.result.url,
                plugin=self.result.plugin,
                downloaded_chapters=downloaded,
                total_chapters=total,
                last_updated=datetime.now().isoformat()
            )

            for i, chapter in enumerate(chapters):
                if not self._is_running:
                    break

                if str(chapter.index) in downloaded:
                    self.chapter_status.emit(chapter.index, "已存在")
                    continue

                self.chapter_status.emit(chapter.index, "下载中...")
                try:
                    content = plugin.get_chapter_content(chapter.url)
                    if content:
                        self.download_manager.save_chapter_content(
                            self.book_save_path,
                            chapter.index,
                            chapter.title,
                            content
                        )
                        downloaded[str(chapter.index)] = chapter.title
                        meta.downloaded_chapters = downloaded
                        meta.last_updated = datetime.now().isoformat()
                        self.download_manager.save_meta(self.book_save_path, meta)
                        self.chapter_status.emit(chapter.index, "✓ 完成")
                    else:
                        self.chapter_status.emit(chapter.index, "内容为空")
                except Exception as e:
                    self.chapter_status.emit(chapter.index, f"✗ 失败")

                self.progress.emit(i + 1, total)

            if len(downloaded) == total:
                self.download_manager.delete_meta(self.book_save_path)

            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))

    def stop(self):
        """Stop the download"""
        self._is_running = False


class DownloadDialog(QDialog):
    """Download progress dialog with modern dark UI"""

    def __init__(self, result: SearchResult, book_save_path: str,
                 download_manager: DownloadManager, parent=None):
        super().__init__(parent)
        self.result = result
        self.book_save_path = book_save_path
        self.download_manager = download_manager
        self.worker = None
        self.chapter_status_map = {}
        self.init_ui()

    def init_ui(self):
        """Initialize the dialog UI"""
        self.setWindowTitle("下载小说")
        self.setMinimumSize(520, 450)
        self.setStyleSheet(get_stylesheet())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])

        # Book info card
        info_card = QWidget()
        info_card.setStyleSheet(f"""
            background-color: {COLORS["bg_secondary"]};
            border-radius: {RADIUS["lg"]}px;
            padding: {SPACING["md"]}px;
        """)
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(SPACING["md"], SPACING["md"], SPACING["md"], SPACING["md"])
        info_layout.setSpacing(SPACING["sm"])

        # Title
        title_label = QLabel(f"📖 {self.result.title}")
        title_label.setStyleSheet(f"""
            color: {COLORS["text_primary"]};
            font-size: {FONT_SIZES["lg"]}px;
            font-weight: bold;
        """)
        info_layout.addWidget(title_label)

        # Author
        author_label = QLabel(f"✍️ {self.result.author}")
        author_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        info_layout.addWidget(author_label)

        # Save path
        path_label = QLabel(f"📁 {self.book_save_path}")
        path_label.setStyleSheet(f"""
            color: {COLORS["text_tertiary"]};
            font-size: {FONT_SIZES["xs"]}px;
        """)
        path_label.setWordWrap(True)
        info_layout.addWidget(path_label)

        layout.addWidget(info_card)

        # Progress section
        progress_label = QLabel("下载进度")
        progress_label.setStyleSheet(f"""
            color: {COLORS["text_secondary"]};
            font-size: {FONT_SIZES["sm"]}px;
            font-weight: bold;
        """)
        layout.addWidget(progress_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS["bg_secondary"]};
                border: none;
                border-radius: {RADIUS["sm"]}px;
                height: 12px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {COLORS["accent"]};
                border-radius: {RADIUS["sm"]}px;
            }}
        """)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("准备下载...")
        self.status_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        layout.addWidget(self.status_label)

        # Chapter list
        self.chapter_list = QListWidget()
        self.chapter_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLORS["bg_secondary"]};
                border: 1px solid {COLORS["border"]};
                border-radius: {RADIUS["md"]}px;
                padding: {SPACING["xs"]}px;
                color: {COLORS["text_primary"]};
            }}
            QListWidget::item {{
                padding: {SPACING["xs"]}px {SPACING["sm"]}px;
                border-radius: {RADIUS["sm"]}px;
                color: {COLORS["text_secondary"]};
            }}
            QListWidget::item:selected {{
                background-color: transparent;
                color: {COLORS["text_primary"]};
            }}
        """)
        layout.addWidget(self.chapter_list, 1)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["bg_tertiary"]};
                border: 1px solid {COLORS["border"]};
                border-radius: {RADIUS["md"]}px;
                padding: 10px 24px;
                color: {COLORS["text_primary"]};
            }}
            QPushButton:hover {{
                background-color: {COLORS["bg_elevated"]};
            }}
        """)
        self.cancel_btn.clicked.connect(self.on_cancel)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

        # Start download
        self.start_download()

    def start_download(self):
        """Start the download worker"""
        self.worker = DownloadWorker(
            self.result,
            self.book_save_path,
            self.download_manager,
            self
        )
        self.worker.progress.connect(self.on_progress)
        self.worker.chapter_status.connect(self.on_chapter_status)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_progress(self, current: int, total: int):
        """Handle progress update"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        percentage = int(current / total * 100) if total > 0 else 0
        self.status_label.setText(f"进度: {current}/{total} 章 ({percentage}%)")

    def on_chapter_status(self, index: int, status: str):
        """Handle chapter status update"""
        if index == -1:
            self.status_label.setText(status)
            return

        if index not in self.chapter_status_map:
            item_text = f"第{index}章 - {status}"
            self.chapter_list.addItem(item_text)
            self.chapter_status_map[index] = self.chapter_list.count() - 1
        else:
            item = self.chapter_list.item(self.chapter_status_map[index])
            item.setText(f"第{index}章 - {status}")

        # Scroll to latest
        self.chapter_list.scrollToItem(
            self.chapter_list.item(self.chapter_status_map[index])
        )

    def on_finished(self):
        """Handle download completion"""
        self.status_label.setText("✓ 下载完成!")
        self.cancel_btn.setText("关闭")
        self.status_label.setStyleSheet(f"color: {COLORS['success']};")

    def on_error(self, error_msg: str):
        """Handle download error"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "错误", f"下载失败: {error_msg}")

    def on_cancel(self):
        """Handle cancel button"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        self.reject()
