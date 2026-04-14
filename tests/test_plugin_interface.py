"""Tests for core/plugin_interface.py - TDD RED phase first"""

import pytest
from enum import Enum


class TestBookStatus:
    """Test BookStatus enum"""

    def test_book_status_enum_exists(self):
        """BookStatus enum should exist"""
        from core.plugin_interface import BookStatus
        assert BookStatus is not None

    def test_book_status_values(self):
        """BookStatus should have SERIALIZING, COMPLETED, UNKNOWN"""
        from core.plugin_interface import BookStatus
        assert BookStatus.SERIALIZING.value == "连载"
        assert BookStatus.COMPLETED.value == "完结"
        assert BookStatus.UNKNOWN.value == "未知"


class TestSearchResult:
    """Test SearchResult dataclass"""

    def test_search_result_can_be_created(self):
        """SearchResult should be creatable with required fields"""
        from core.plugin_interface import SearchResult, BookStatus
        result = SearchResult(
            title="凡人修仙传",
            author="忘语",
            status=BookStatus.COMPLETED,
            url="https://example.com/1",
            plugin="3yt"
        )
        assert result.title == "凡人修仙传"
        assert result.author == "忘语"
        assert result.status == BookStatus.COMPLETED
        assert result.url == "https://example.com/1"
        assert result.plugin == "3yt"


class TestChapterInfo:
    """Test ChapterInfo dataclass"""

    def test_chapter_info_can_be_created(self):
        """ChapterInfo should be creatable with required fields"""
        from core.plugin_interface import ChapterInfo
        chapter = ChapterInfo(
            index=1,
            title="第一章 黄皮葫芦",
            url="https://example.com/chapter/1"
        )
        assert chapter.index == 1
        assert chapter.title == "第一章 黄皮葫芦"
        assert chapter.url == "https://example.com/chapter/1"


class TestNovelPlugin:
    """Test NovelPlugin abstract base class"""

    def test_novel_plugin_is_abc(self):
        """NovelPlugin should be an abstract base class"""
        from core.plugin_interface import NovelPlugin
        from abc import ABC
        assert issubclass(NovelPlugin, ABC)

    def test_novel_plugin_requires_name_property(self):
        """NovelPlugin should have abstract name property"""
        from core.plugin_interface import NovelPlugin
        # name should be abstract property
        plugin = NovelPlugin.__dict__['name']
        assert plugin is not None

    def test_novel_plugin_requires_domain_property(self):
        """NovelPlugin should have abstract domain property"""
        from core.plugin_interface import NovelPlugin
        # domain should be abstract property
        plugin = NovelPlugin.__dict__['domain']
        assert plugin is not None

    def test_novel_plugin_requires_abstract_methods(self):
        """NovelPlugin should have abstract methods: search, get_chapter_list, get_chapter_content"""
        from core.plugin_interface import NovelPlugin
        assert hasattr(NovelPlugin, 'search')
        assert hasattr(NovelPlugin, 'get_chapter_list')
        assert hasattr(NovelPlugin, 'get_chapter_content')
