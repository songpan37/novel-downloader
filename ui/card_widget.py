"""Card widget for displaying search results - Modern Dark Theme"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import Signal, Qt
from core.plugin_interface import SearchResult
from ui.theme import COLORS, SPACING, RADIUS, FONT_SIZES


class CardWidget(QWidget):
    """Card widget to display a single search result with modern dark styling"""

    double_clicked = Signal(SearchResult)

    def __init__(self, result: SearchResult, parent=None):
        super().__init__(parent)
        self.result = result
        self._is_hovered = False
        self.init_ui()

    def init_ui(self):
        """Initialize the card UI with modern dark theme"""
        self.setMinimumSize(220, 160)
        self.setMaximumSize(220, 160)
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Card style
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS["card_bg"]};
                border: 1px solid {COLORS["card_border"]};
                border-radius: {RADIUS["lg"]}px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["md"], SPACING["md"], SPACING["md"], SPACING["md"])
        layout.setSpacing(SPACING["sm"])

        # Title - bold, white
        self.title_label = QLabel(self.result.title)
        self.title_label.setStyleSheet(f"""
            color: {COLORS["text_primary"]};
            font-size: {FONT_SIZES["md"]}px;
            font-weight: bold;
        """)
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.addWidget(self.title_label, 1)

        # Author - secondary color
        self.author_label = QLabel(self.result.author)
        self.author_label.setStyleSheet(f"""
            color: {COLORS["text_secondary"]};
            font-size: {FONT_SIZES["sm"]}px;
        """)
        layout.addWidget(self.author_label)

        # Status badge
        status_color = COLORS["success"] if self.result.status.value == "完结" else COLORS["warning"]
        self.status_label = QLabel(f"● {self.result.status.value}")
        self.status_label.setStyleSheet(f"""
            color: {status_color};
            font-size: {FONT_SIZES["xs"]}px;
        """)
        layout.addWidget(self.status_label)

        # Plugin source
        self.plugin_label = QLabel(f"[{self.result.plugin}]")
        self.plugin_label.setStyleSheet(f"""
            color: {COLORS["accent"]};
            font-size: {FONT_SIZES["xs"]}px;
        """)
        layout.addWidget(self.plugin_label)

    def enterEvent(self, event):
        """Handle mouse enter - show hover state"""
        self._is_hovered = True
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS["card_bg_hover"]};
                border: 1px solid {COLORS["accent"]};
                border-radius: {RADIUS["lg"]}px;
            }}
        """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave - restore normal state"""
        self._is_hovered = False
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS["card_bg"]};
                border: 1px solid {COLORS["card_border"]};
                border-radius: {RADIUS["lg"]}px;
            }}
        """)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Visual feedback on press"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS["bg_tertiary"]};
                border: 1px solid {COLORS["accent_pressed"]};
                border-radius: {RADIUS["lg"]}px;
            }}
        """)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Restore hover state on release"""
        if self._is_hovered:
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {COLORS["card_bg_hover"]};
                    border: 1px solid {COLORS["accent"]};
                    border-radius: {RADIUS["lg"]}px;
                }}
            """)
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Emit double clicked signal"""
        self.double_clicked.emit(self.result)
