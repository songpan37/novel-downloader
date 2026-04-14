"""Tests for core/download_manager.py - TDD RED phase first"""

import pytest
import os
import tempfile
import json
from unittest.mock import MagicMock, patch
from datetime import datetime


class TestDownloadMeta:
    """Test DownloadMeta dataclass"""

    def test_download_meta_can_be_created(self):
        """DownloadMeta should be creatable"""
        from core.download_manager import DownloadMeta
        meta = DownloadMeta(
            book_url="https://example.com/book/1",
            plugin="3yt",
            downloaded_chapters={"1": "第一章", "2": "第二章"},
            total_chapters=100,
            last_updated="2026-04-14T20:30:00"
        )
        assert meta.book_url == "https://example.com/book/1"
        assert meta.plugin == "3yt"
        assert meta.downloaded_chapters == {"1": "第一章", "2": "第二章"}
        assert meta.total_chapters == 100


class TestDownloadManager:
    """Test DownloadManager class"""

    def test_load_meta_returns_none_when_not_exists(self):
        """load_meta should return None when meta file doesn't exist"""
        from core.download_manager import DownloadManager
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DownloadManager(tmpdir)
            meta = manager.load_meta("https://example.com/book/1", "3yt")
            assert meta is None

    def test_save_and_load_meta_preserves_data(self):
        """save_meta and load_meta should preserve data"""
        from core.download_manager import DownloadManager, DownloadMeta
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DownloadManager(tmpdir)
            book_path = os.path.join(tmpdir, "test_book")
            os.makedirs(book_path)

            meta = DownloadMeta(
                book_url="https://example.com/book/1",
                plugin="3yt",
                downloaded_chapters={"1": "第一章", "2": "第二章"},
                total_chapters=100,
                last_updated="2026-04-14T20:30:00"
            )
            manager.save_meta(book_path, meta)
            loaded = manager.load_meta("https://example.com/book/1", "3yt")

            assert loaded is not None
            assert loaded.book_url == meta.book_url
            assert loaded.plugin == meta.plugin
            assert loaded.downloaded_chapters == meta.downloaded_chapters
            assert loaded.total_chapters == meta.total_chapters

    def test_delete_meta_removes_file(self):
        """delete_meta should remove the meta file"""
        from core.download_manager import DownloadManager, DownloadMeta
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DownloadManager(tmpdir)
            book_path = os.path.join(tmpdir, "test_book")
            os.makedirs(book_path)

            meta = DownloadMeta(
                book_url="https://example.com/book/1",
                plugin="3yt",
                downloaded_chapters={"1": "第一章"},
                total_chapters=100,
                last_updated="2026-04-14T20:30:00"
            )
            manager.save_meta(book_path, meta)
            assert manager.load_meta("https://example.com/book/1", "3yt") is not None

            manager.delete_meta(book_path)
            assert manager.load_meta("https://example.com/book/1", "3yt") is None

    def test_get_book_save_path(self):
        """get_book_save_path should return correct path"""
        from core.download_manager import DownloadManager
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DownloadManager(tmpdir)
            path = manager.get_book_save_path("E:\\novel", "玄幻", "凡人修仙传")
            assert path == os.path.join("E:\\novel", "玄幻", "凡人修仙传")

    def test_get_chapter_file_path(self):
        """get_chapter_file_path should return correct path"""
        from core.download_manager import DownloadManager
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DownloadManager(tmpdir)
            book_path = os.path.join(tmpdir, "book")
            os.makedirs(book_path)
            chapter_path = manager.get_chapter_file_path(book_path, 1, "第一章 黄皮葫芦")
            # Should contain chapter number and title
            assert "第1章" in chapter_path or "1" in chapter_path

    def test_is_chapter_downloaded(self):
        """is_chapter_downloaded should check if chapter exists"""
        from core.download_manager import DownloadManager, DownloadMeta
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DownloadManager(tmpdir)
            book_path = os.path.join(tmpdir, "test_book")
            os.makedirs(book_path)

            meta = DownloadMeta(
                book_url="https://example.com/book/1",
                plugin="3yt",
                downloaded_chapters={"1": "第一章", "2": "第二章"},
                total_chapters=100,
                last_updated="2026-04-14T20:30:00"
            )
            manager.save_meta(book_path, meta)

            assert manager.is_chapter_downloaded(book_path, 1) is True
            assert manager.is_chapter_downloaded(book_path, 3) is False

    def test_save_chapter_content(self):
        """save_chapter_content should write file with UTF-8 encoding"""
        from core.download_manager import DownloadManager
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DownloadManager(tmpdir)
            book_path = os.path.join(tmpdir, "test_book")
            os.makedirs(book_path)

            content = "这是章节内容，包含中文"
            chapter_path = manager.save_chapter_content(book_path, 1, "第一章", content)

            assert os.path.exists(chapter_path)
            with open(chapter_path, 'r', encoding='utf-8') as f:
                saved_content = f.read()
            assert saved_content == content
