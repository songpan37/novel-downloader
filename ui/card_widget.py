"""Card widget for displaying search results - Simple Clean Style"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Signal, Qt
from core.plugin_interface import SearchResult


class CardWidget(QWidget):
    """Card widget to display a single search result with simple clean styling."""

    double_clicked = Signal(SearchResult)

    def __init__(self, result: SearchResult, parent=None):
        super().__init__(parent)
        self.result = result
        self._is_hovered = False
        self.init_ui()

    def init_ui(self):
        """Initialize the card UI with simple clean style."""
        self.setMinimumHeight(80)
        self.setCursor(Qt.PointingHandCursor)

        # Base style
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: 1px solid #404040;
                border-radius: 6px;
            }
            QWidget:hover {
                border-color: #606060;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        # Book title
        self.title_label = QLabel(self.result.title)
        self.title_label.setStyleSheet("""
            color: #e0e0e0;
            font-size: 15px;
            font-weight: bold;
        """)
        self.title_label.setWordWrap(False)
        layout.addWidget(self.title_label)

        # Author row
        author_layout = QHBoxLayout()
        author_layout.setSpacing(8)

        author_label = QLabel("作者:")
        author_label.setStyleSheet("color: #808080; font-size: 13px;")
        author_layout.addWidget(author_label)

        self.author_label = QLabel(self.result.author)
        self.author_label.setStyleSheet("color: #a0a0a0; font-size: 13px;")
        author_layout.addWidget(self.author_label)

        author_layout.addStretch()

        # Status
        status_text = "完结" if self.result.status.value == "完结" else "连载"
        status_color = "#4a9f4a" if status_text == "完结" else "#c9a227"
        self.status_label = QLabel(status_text)
        self.status_label.setStyleSheet(f"""
            color: {status_color};
            font-size: 12px;
        """)
        author_layout.addWidget(self.status_label)

        # Source
        source_label = QLabel(f"来源: {self.result.plugin}")
        source_label.setStyleSheet("color: #606060; font-size: 12px;")
        author_layout.addWidget(source_label)

        layout.addLayout(author_layout)

    def enterEvent(self, event):
        """Handle mouse enter."""
        self._is_hovered = True
        self.setStyleSheet("""
            QWidget {
                background-color: #2a2a2a;
                border: 1px solid #606060;
                border-radius: 6px;
            }
        """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave."""
        self._is_hovered = False
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: 1px solid #404040;
                border-radius: 6px;
            }
        """)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Visual feedback on press."""
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border: 1px solid #808080;
                border-radius: 6px;
            }
        """)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Restore hover state on release."""
        if self._is_hovered:
            self.setStyleSheet("""
                QWidget {
                    background-color: #2a2a2a;
                    border: 1px solid #606060;
                    border-radius: 6px;
                }
            """)
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Emit double clicked signal."""
        self.double_clicked.emit(self.result)