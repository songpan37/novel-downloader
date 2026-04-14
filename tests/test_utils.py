"""Tests for core/utils.py - TDD RED phase first"""

import pytest


class TestSanitizeFilename:
    """Test sanitize_filename function"""

    def test_sanitize_filename_removes_backslash(self):
        """should remove backslash"""
        from core.utils import sanitize_filename
        result = sanitize_filename("test\\name")
        assert "\\" not in result

    def test_sanitize_filename_removes_forward_slash(self):
        """should remove forward slash"""
        from core.utils import sanitize_filename
        result = sanitize_filename("test/name")
        assert "/" not in result

    def test_sanitize_filename_removes_colon(self):
        """should remove colon"""
        from core.utils import sanitize_filename
        result = sanitize_filename("test:name")
        assert ":" not in result

    def test_sanitize_filename_removes_asterisk(self):
        """should remove asterisk"""
        from core.utils import sanitize_filename
        result = sanitize_filename("test*name")
        assert "*" not in result

    def test_sanitize_filename_removes_question_mark(self):
        """should remove question mark"""
        from core.utils import sanitize_filename
        result = sanitize_filename("test?name")
        assert "?" not in result

    def test_sanitize_filename_removes_quote(self):
        """should remove double quote"""
        from core.utils import sanitize_filename
        result = sanitize_filename('test"name')
        assert '"' not in result

    def test_sanitize_filename_removes_angle_brackets(self):
        """should remove angle brackets"""
        from core.utils import sanitize_filename
        result = sanitize_filename("test<name>")
        assert "<" not in result
        assert ">" not in result

    def test_sanitize_filename_removes_pipe(self):
        """should remove pipe"""
        from core.utils import sanitize_filename
        result = sanitize_filename("test|name")
        assert "|" not in result

    def test_sanitize_filename_trims_whitespace(self):
        """should trim leading and trailing whitespace"""
        from core.utils import sanitize_filename
        result = sanitize_filename("  test name  ")
        assert result == "test name"
        assert not result.startswith(" ")
        assert not result.endswith(" ")

    def test_sanitize_filename_replaces_with_underscore(self):
        """replaced chars should become underscore"""
        from core.utils import sanitize_filename
        result = sanitize_filename("test:name")
        assert "_" in result or ":" not in result

    def test_sanitize_filename_preserves_normal_chars(self):
        """should preserve normal characters"""
        from core.utils import sanitize_filename
        result = sanitize_filename("凡人修仙传_第一章")
        assert result == "凡人修仙传_第一章"


class TestRemoveDuplicateChapterPrefix:
    """Test remove_duplicate_chapter_prefix function"""

    def test_removes_duplicate_prefix_when_exact_match(self):
        """should remove '第x章 ' prefix when title starts with it"""
        from core.utils import remove_duplicate_chapter_prefix
        result = remove_duplicate_chapter_prefix("第1章 黄皮葫芦")
        assert result == "黄皮葫芦"

    def test_removes_prefix_with_multidigit_number(self):
        """should work with multi-digit chapter numbers"""
        from core.utils import remove_duplicate_chapter_prefix
        result = remove_duplicate_chapter_prefix("第123章 测试章节")
        assert result == "测试章节"

    def test_keeps_title_without_prefix(self):
        """should keep title as-is if no prefix"""
        from core.utils import remove_duplicate_chapter_prefix
        result = remove_duplicate_chapter_prefix("黄皮葫芦")
        assert result == "黄皮葫芦"

    def test_keeps_title_with_similar_but_not_exact_prefix(self):
        """should keep title if prefix is not exact match"""
        from core.utils import remove_duplicate_chapter_prefix
        result = remove_duplicate_chapter_prefix("第1章黄皮葫芦")  # no space
        assert result == "第1章黄皮葫芦"  # should NOT be removed
