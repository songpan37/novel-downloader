"""Theme constants for the application"""

# Color Palette - Dark Mode
COLORS = {
    # Backgrounds
    "bg_primary": "#0f0f0f",       # Main background
    "bg_secondary": "#1a1a1a",     # Cards, panels
    "bg_tertiary": "#242424",      # Input fields, hover states
    "bg_elevated": "#2d2d2d",      # Elevated elements

    # Text
    "text_primary": "#ffffff",     # Primary text
    "text_secondary": "#a0a0a0",   # Secondary text
    "text_tertiary": "#666666",    # Disabled/hint text

    # Accent
    "accent": "#6366f1",           # Indigo accent
    "accent_hover": "#818cf8",     # Accent hover
    "accent_pressed": "#4f46e5",   # Accent pressed

    # Status
    "success": "#22c55e",          # Success green
    "warning": "#f59e0b",          # Warning amber
    "error": "#ef4444",            # Error red
    "info": "#3b82f6",             # Info blue

    # Borders
    "border": "#333333",            # Default border
    "border_hover": "#444444",      # Hover border

    # Card specific
    "card_bg": "#1a1a1a",
    "card_bg_hover": "#242424",
    "card_border": "#2d2d2d",
}

# Spacing (8dp grid)
SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32,
}

# Border radius
RADIUS = {
    "sm": 4,
    "md": 8,
    "lg": 12,
    "xl": 16,
}

# Typography
FONT_SIZES = {
    "xs": 11,
    "sm": 12,
    "md": 14,
    "lg": 16,
    "xl": 18,
    "2xl": 24,
}

# Animation durations
DURATION = {
    "fast": 150,
    "normal": 250,
    "slow": 350,
}


def get_stylesheet() -> str:
    """Get global stylesheet for dark theme"""
    return f"""
    QWidget {{
        background-color: {COLORS["bg_primary"]};
        color: {COLORS["text_primary"]};
        font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
        font-size: {FONT_SIZES["md"]}px;
    }}

    QMainWindow {{
        background-color: {COLORS["bg_primary"]};
    }}

    /* Scrollbars */
    QScrollBar:vertical {{
        background-color: {COLORS["bg_primary"]};
        width: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background-color: {COLORS["bg_tertiary"]};
        border-radius: 4px;
        min-height: 40px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS["border_hover"]};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        background-color: {COLORS["bg_primary"]};
        height: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal {{
        background-color: {COLORS["bg_tertiary"]};
        border-radius: 4px;
        min-width: 40px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background-color: {COLORS["border_hover"]};
    }}

    /* Buttons */
    QPushButton {{
        background-color: {COLORS["bg_tertiary"]};
        color: {COLORS["text_primary"]};
        border: 1px solid {COLORS["border"]};
        border-radius: {RADIUS["md"]}px;
        padding: {SPACING["sm"]}px {SPACING["md"]}px;
        font-size: {FONT_SIZES["md"]}px;
        min-height: 32px;
    }}
    QPushButton:hover {{
        background-color: {COLORS["bg_elevated"]};
        border-color: {COLORS["border_hover"]};
    }}
    QPushButton:pressed {{
        background-color: {COLORS["bg_tertiary"]};
    }}
    QPushButton:disabled {{
        background-color: {COLORS["bg_secondary"]};
        color: {COLORS["text_tertiary"]};
        border-color: {COLORS["bg_secondary"]};
    }}

    /* Primary Button */
    QPushButton[class="primary"] {{
        background-color: {COLORS["accent"]};
        border-color: {COLORS["accent"]};
        color: white;
    }}
    QPushButton[class="primary"]:hover {{
        background-color: {COLORS["accent_hover"]};
        border-color: {COLORS["accent_hover"]};
    }}
    QPushButton[class="primary"]:pressed {{
        background-color: {COLORS["accent_pressed"]};
    }}

    /* Line Edit */
    QLineEdit {{
        background-color: {COLORS["bg_secondary"]};
        color: {COLORS["text_primary"]};
        border: 1px solid {COLORS["border"]};
        border-radius: {RADIUS["md"]}px;
        padding: {SPACING["sm"]}px {SPACING["md"]}px;
        font-size: {FONT_SIZES["md"]}px;
        min-height: 36px;
    }}
    QLineEdit:hover {{
        border-color: {COLORS["border_hover"]};
    }}
    QLineEdit:focus {{
        border-color: {COLORS["accent"]};
    }}
    QLineEdit::placeholder {{
        color: {COLORS["text_tertiary"]};
    }}

    /* ComboBox */
    QComboBox {{
        background-color: {COLORS["bg_secondary"]};
        color: {COLORS["text_primary"]};
        border: 1px solid {COLORS["border"]};
        border-radius: {RADIUS["md"]}px;
        padding: {SPACING["sm"]}px {SPACING["md"]}px;
        font-size: {FONT_SIZES["md"]}px;
        min-height: 36px;
    }}
    QComboBox:hover {{
        border-color: {COLORS["border_hover"]};
    }}
    QComboBox:focus {{
        border-color: {COLORS["accent"]};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid {COLORS["text_secondary"]};
        margin-right: 8px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLORS["bg_secondary"]};
        color: {COLORS["text_primary"]};
        border: 1px solid {COLORS["border"]};
        selection-background-color: {COLORS["accent"]};
        padding: {SPACING["xs"]}px;
    }}

    /* Labels */
    QLabel {{
        color: {COLORS["text_primary"]};
        font-size: {FONT_SIZES["md"]}px;
    }}
    QLabel[class="secondary"] {{
        color: {COLORS["text_secondary"]};
    }}
    QLabel[class="title"] {{
        font-size: {FONT_SIZES["xl"]}px;
        font-weight: bold;
    }}

    /* Status Bar */
    QStatusBar {{
        background-color: {COLORS["bg_secondary"]};
        color: {COLORS["text_secondary"]};
        border-top: 1px solid {COLORS["border"]};
    }}

    /* Message Box */
    QMessageBox {{
        background-color: {COLORS["bg_primary"]};
    }}
    QMessageBox QLabel {{
        color: {COLORS["text_primary"]};
    }}

    /* Dialog */
    QDialog {{
        background-color: {COLORS["bg_primary"]};
    }}

    /* Progress Bar */
    QProgressBar {{
        background-color: {COLORS["bg_secondary"]};
        border: none;
        border-radius: {RADIUS["sm"]}px;
        height: 8px;
        text-align: center;
    }}
    QProgressBar::chunk {{
        background-color: {COLORS["accent"]};
        border-radius: {RADIUS["sm"]}px;
    }}

    /* List Widget */
    QListWidget {{
        background-color: {COLORS["bg_secondary"]};
        color: {COLORS["text_primary"]};
        border: 1px solid {COLORS["border"]};
        border-radius: {RADIUS["md"]}px;
        padding: {SPACING["xs"]}px;
    }}
    QListWidget::item {{
        padding: {SPACING["sm"]}px;
        border-radius: {RADIUS["sm"]}px;
    }}
    QListWidget::item:selected {{
        background-color: {COLORS["accent"]};
    }}
    QListWidget::item:hover {{
        background-color: {COLORS["bg_tertiary"]};
    }}
    """
