#!/usr/bin/env python3
"""Novel Downloader - Main entry point"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Suppress libpng warnings from Qt's image plugins by redirecting stderr
# These warnings are printed directly to stderr by the C libpng library
stderr_fd = os.dup(2)
devnull = os.open(os.devnull, os.O_WRONLY)
os.dup2(devnull, 2)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QLoggingCategory

# Restore stderr after Qt image plugins have been loaded
os.dup2(stderr_fd, 2)
os.close(devnull)
os.close(stderr_fd)

# Suppress Qt warnings about image plugins
QLoggingCategory.setFilterRules("qt.imageio.*.warning=false")

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
