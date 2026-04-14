"""Tests for core/config.py - TDD RED phase first"""

import pytest
import os
import tempfile
import json


class TestUserConfig:
    """Test UserConfig dataclass"""

    def test_user_config_can_be_created(self):
        """UserConfig should be creatable with required fields"""
        from core.config import UserConfig
        config = UserConfig(
            root_dir="E:\\novel",
            categories=["玄幻", "都市"],
            last_category="玄幻"
        )
        assert config.root_dir == "E:\\novel"
        assert config.categories == ["玄幻", "都市"]
        assert config.last_category == "玄幻"


class TestConfigManager:
    """Test ConfigManager class"""

    def test_load_returns_default_when_no_file(self):
        """load should return default config when file doesn't exist"""
        from core.config import ConfigManager
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "config.json")
            manager = ConfigManager(config_file)
            config = manager.load()
            assert config.root_dir == ""
            assert config.categories == []
            assert config.last_category == ""

    def test_save_and_load_preserves_config(self):
        """save and load should preserve config"""
        from core.config import ConfigManager, UserConfig
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "config.json")
            manager = ConfigManager(config_file)
            original = UserConfig(
                root_dir="E:\\novel",
                categories=["玄幻", "都市"],
                last_category="玄幻"
            )
            manager.save(original)
            loaded = manager.load()
            assert loaded.root_dir == original.root_dir
            assert loaded.categories == original.categories
            assert loaded.last_category == original.last_category

    def test_add_category(self):
        """add_category should add new category"""
        from core.config import ConfigManager
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "config.json")
            manager = ConfigManager(config_file)
            manager.add_category("科幻")
            config = manager.load()
            assert "科幻" in config.categories

    def test_add_category_prevents_duplicates(self):
        """add_category should not add duplicate"""
        from core.config import ConfigManager
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "config.json")
            manager = ConfigManager(config_file)
            manager.add_category("玄幻")
            manager.add_category("玄幻")  # duplicate
            config = manager.load()
            assert config.categories.count("玄幻") == 1

    def test_remove_category(self):
        """remove_category should remove existing category"""
        from core.config import ConfigManager
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "config.json")
            manager = ConfigManager(config_file)
            manager.add_category("玄幻")
            manager.remove_category("玄幻")
            config = manager.load()
            assert "玄幻" not in config.categories

    def test_set_root_dir(self):
        """set_root_dir should update root directory"""
        from core.config import ConfigManager
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "config.json")
            manager = ConfigManager(config_file)
            manager.set_root_dir("E:\\novel")
            config = manager.load()
            assert config.root_dir == "E:\\novel"
