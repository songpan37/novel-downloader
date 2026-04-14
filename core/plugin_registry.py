"""Plugin registry for managing novel plugins"""

from typing import List, Dict
from core.plugin_interface import NovelPlugin


class PluginRegistry:
    """Singleton registry for managing novel plugins"""

    _instance = None

    def __init__(self):
        self._plugins: Dict[str, NovelPlugin] = {}

    @classmethod
    def get_instance(cls):
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(self, plugin: NovelPlugin):
        """Register a plugin"""
        self._plugins[plugin.name] = plugin

    def get_plugin(self, name: str) -> NovelPlugin:
        """Get a plugin by name"""
        return self._plugins.get(name)

    def list_plugins(self) -> List[str]:
        """List all registered plugin names"""
        return list(self._plugins.keys())
