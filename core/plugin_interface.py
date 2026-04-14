"""Plugin interface definitions for novel downloader"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List


class BookStatus(Enum):
    """Book status enumeration"""
    SERIALIZING = "连载"
    COMPLETED = "完结"
    UNKNOWN = "未知"


@dataclass
class SearchResult:
    """Search result for a novel"""
    title: str           # 书名
    author: str          # 作者
    status: BookStatus   # 状态（使用 BookStatus 枚举）
    url: str             # 书籍详情页URL
    plugin: str          # 来源插件名


@dataclass
class ChapterInfo:
    """Chapter information"""
    index: int       # 章节序号
    title: str       # 章节名（原始）
    url: str         # 章节URL


class NovelPlugin(ABC):
    """Abstract base class for novel website plugins"""

    @property
    @abstractmethod
    def name(self) -> str:
        """插件名称，如 '3yt'"""
        pass

    @property
    @abstractmethod
    def domain(self) -> str:
        """网站域名，如 'https://www.3yt.org'"""
        pass

    @abstractmethod
    def search(self, keyword: str) -> List[SearchResult]:
        """根据关键字搜索小说"""
        pass

    @abstractmethod
    def get_chapter_list(self, book_url: str) -> List[ChapterInfo]:
        """获取书籍的章节列表"""
        pass

    @abstractmethod
    def get_chapter_content(self, chapter_url: str) -> str:
        """获取单个章节的纯文本内容（不含标题）"""
        pass
