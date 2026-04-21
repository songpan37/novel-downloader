"""Download manager for handling chapter downloads and resume support"""

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Optional

from core.utils import sanitize_filename, remove_duplicate_chapter_prefix


META_FILENAME = ".download_meta.json"


@dataclass
class DownloadMeta:
    """Download metadata for resume support"""
    book_url: str
    plugin: str
    downloaded_chapters: Dict[str, str]  # {chapter_index: chapter_title}
    total_chapters: int
    last_updated: str


class DownloadManager:
    """Manages download operations with resume support"""

    def __init__(self, root_dir: str):
        self.root_dir = root_dir

    def get_meta_file_path(self, book_path: str) -> str:
        """Get the path to the meta file for a book"""
        return os.path.join(book_path, META_FILENAME)

    def load_meta(self, book_url: str, plugin: str) -> Optional[DownloadMeta]:
        """Load download metadata from book path"""
        # Search for meta file in root_dir
        if not os.path.exists(self.root_dir):
            return None

        for item in os.listdir(self.root_dir):
            item_path = os.path.join(self.root_dir, item)
            if os.path.isdir(item_path):
                meta_path = self.get_meta_file_path(item_path)
                if os.path.exists(meta_path):
                    try:
                        with open(meta_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        if data.get('book_url') == book_url and data.get('plugin') == plugin:
                            return DownloadMeta(
                                book_url=data['book_url'],
                                plugin=data['plugin'],
                                downloaded_chapters=data['downloaded_chapters'],
                                total_chapters=data['total_chapters'],
                                last_updated=data['last_updated']
                            )
                    except (json.JSONDecodeError, KeyError):
                        continue
        return None

    def save_meta(self, book_path: str, meta: DownloadMeta):
        """Save download metadata"""
        os.makedirs(book_path, exist_ok=True)
        meta_path = self.get_meta_file_path(book_path)
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(meta), f, indent=4, ensure_ascii=False)

    def delete_meta(self, book_path: str):
        """Delete download metadata"""
        meta_path = self.get_meta_file_path(book_path)
        if os.path.exists(meta_path):
            os.remove(meta_path)

    def get_book_save_path(self, root_dir: str, category: str, book_name: str) -> str:
        """Get the save path for a book"""
        return os.path.join(root_dir, category, book_name)

    def get_chapter_file_path(self, book_path: str, chapter_index: int, chapter_title: str) -> str:
        """Get the file path for a chapter"""
        # Remove duplicate prefix if exists
        clean_title = remove_duplicate_chapter_prefix(chapter_title)
        safe_title = sanitize_filename(clean_title)
        filename = f"第{chapter_index}章 {safe_title}.txt"
        return os.path.join(book_path, filename)

    def find_chapter_file_path(self, book_path: str, chapter_index: int) -> str:
        """Find the actual file path for a chapter, checking various title possibilities.

        This handles cases where the chapter was saved with a different title than expected.
        Returns the path if found, empty string if not found.
        """
        # Try common patterns
        patterns = [
            f"第{chapter_index}章 *.txt",  # Any title
            f"第{chapter_index}章.txt",     # No title
        ]

        for pattern in patterns:
            import fnmatch
            for filename in os.listdir(book_path):
                if fnmatch.fnmatch(filename, pattern):
                    return os.path.join(book_path, filename)

        return ""

    def is_chapter_downloaded(self, book_path: str, chapter_index: int) -> bool:
        """Check if a chapter has been downloaded"""
        return self.find_chapter_file_path(book_path, chapter_index) != ""

    def save_chapter_content(self, book_path: str, chapter_index: int, chapter_title: str, content: str) -> str:
        """Save chapter content to file"""
        os.makedirs(book_path, exist_ok=True)
        chapter_path = self.get_chapter_file_path(book_path, chapter_index, chapter_title)
        with open(chapter_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return chapter_path
