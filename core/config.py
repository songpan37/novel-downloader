"""Configuration management for novel downloader"""

import json
import os
from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass
class UserConfig:
    """User configuration"""
    root_dir: str                # 存储根目录
    categories: List[str]       # 已有类别列表
    last_category: str          # 上次使用的类别


class ConfigManager:
    """Manages user configuration persistence"""

    def __init__(self, config_file: str):
        self.config_file = config_file

    def load(self) -> UserConfig:
        """Load configuration from file, returns default if not exists"""
        if not os.path.exists(self.config_file):
            return UserConfig(root_dir="", categories=[], last_category="")

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return UserConfig(
                root_dir=data.get('root_dir', ''),
                categories=data.get('categories', []),
                last_category=data.get('last_category', '')
            )
        except (json.JSONDecodeError, KeyError):
            return UserConfig(root_dir="", categories=[], last_category="")

    def save(self, config: UserConfig):
        """Save configuration to file"""
        dir_path = os.path.dirname(self.config_file)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(config), f, indent=4, ensure_ascii=False)

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
