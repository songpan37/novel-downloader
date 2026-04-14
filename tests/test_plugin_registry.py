"""Tests for core/plugin_registry.py - TDD RED phase first"""

import pytest
from unittest.mock import MagicMock


class TestPluginRegistry:
    """Test PluginRegistry singleton"""

    def test_get_instance_returns_singleton(self):
        """get_instance should return the same instance"""
        from core.plugin_registry import PluginRegistry
        instance1 = PluginRegistry.get_instance()
        instance2 = PluginRegistry.get_instance()
        assert instance1 is instance2

    def test_register_adds_plugin(self):
        """register should add plugin to registry"""
        from core.plugin_registry import PluginRegistry
        # Create fresh instance for this test
        registry = PluginRegistry()
        mock_plugin = MagicMock()
        mock_plugin.name = "test_plugin"
        registry.register(mock_plugin)
        assert registry.get_plugin("test_plugin") is mock_plugin

    def test_get_plugin_returns_registered(self):
        """get_plugin should return the registered plugin"""
        from core.plugin_registry import PluginRegistry
        registry = PluginRegistry()
        mock_plugin = MagicMock()
        mock_plugin.name = "my_plugin"
        registry.register(mock_plugin)
        assert registry.get_plugin("my_plugin") is mock_plugin

    def test_get_plugin_returns_none_for_unknown(self):
        """get_plugin should return None for unknown plugin"""
        from core.plugin_registry import PluginRegistry
        registry = PluginRegistry()
        assert registry.get_plugin("nonexistent") is None

    def test_list_plugins_returns_all_names(self):
        """list_plugins should return list of all plugin names"""
        from core.plugin_registry import PluginRegistry
        registry = PluginRegistry()
        mock1 = MagicMock()
        mock1.name = "plugin1"
        mock2 = MagicMock()
        mock2.name = "plugin2"
        registry.register(mock1)
        registry.register(mock2)
        plugins = registry.list_plugins()
        assert "plugin1" in plugins
        assert "plugin2" in plugins
