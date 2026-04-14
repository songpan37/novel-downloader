#!/usr/bin/env python3
"""Novel Downloader - Main entry point"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    """Main application entry"""
    app = QApplication(sys.argv)
    app.setApplicationName("小说下载器")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
