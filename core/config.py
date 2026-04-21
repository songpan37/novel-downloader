"""Configuration management for novel downloader"""

import json
import os
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict


DEFAULT_CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

@dataclass
class UserConfig:
    """User configuration"""
    root_dir: str                           # 存储根目录
    plugin_urls: Dict[str, str]             # 插件URL配置 {plugin_name: url}
    last_category: str                     # 上次使用的类别
    browser_headless: bool = True          # 浏览器是否无头模式（默认无头）
    chrome_path: str = ""                   # Chrome浏览器路径
    categories: List[str] = field(default_factory=list)


class ConfigManager:
    """Manages user configuration persistence"""

    def __init__(self, config_file: str):
        self.config_file = config_file

    def load(self) -> UserConfig:
        """Load configuration from file, returns default if not exists"""
        if not os.path.exists(self.config_file):
            return UserConfig(
                root_dir="",
                plugin_urls={},
                last_category="",
                browser_headless=True,
                chrome_path="",
                categories=[]
            )

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return UserConfig(
                root_dir=data.get('root_dir', ''),
                plugin_urls=data.get('plugin_urls', {}),
                last_category=data.get('last_category', ''),
                browser_headless=data.get('browser_headless', True),
                chrome_path=data.get('chrome_path', ''),
                categories=data.get('categories', [])
            )
        except (json.JSONDecodeError, KeyError):
            return UserConfig(
                root_dir="",
                plugin_urls={},
                last_category="",
                browser_headless=True,
                chrome_path="",
                categories=[]
            )

    def save(self, config: UserConfig):
        """Save configuration to file"""
        dir_path = os.path.dirname(self.config_file)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(config), f, indent=4, ensure_ascii=False)

    def set_root_dir(self, root_dir: str):
        """Set the root directory"""
        config = self.load()
        config.root_dir = root_dir
        self.save(config)

    def set_last_category(self, category: str):
        """Set the last used category"""
        config = self.load()
        config.last_category = category
        self.save(config)

    def get_plugin_url(self, plugin_name: str) -> Optional[str]:
        """Get the configured URL for a plugin"""
        config = self.load()
        return config.plugin_urls.get(plugin_name)

    def set_plugin_url(self, plugin_name: str, url: str):
        """Set the URL for a plugin"""
        config = self.load()
        config.plugin_urls[plugin_name] = url
        self.save(config)

    def add_category(self, category: str):
        """Add a new category"""
        config = self.load()
        if category not in config.categories:
            config.categories.append(category)
            self.save(config)

    def remove_category(self, category: str):
        """Remove a category"""
        config = self.load()
        if category in config.categories:
            config.categories.remove(category)
            self.save(config)
