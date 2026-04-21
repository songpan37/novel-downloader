"""bqg plugin for novel downloader - 笔趣阁

Based on docs/coding-plan/bqg.md - HTTP请求流程

API endpoints:
- Search: https://www.bqg655.cc/api/search?q={keyword}
- Book info: https://apibi.cc/api/book?id={book_id}
- Chapter content: https://apibi.cc/api/chapter?id={book_id}&chapterid={chapter_num}
"""

import json
from typing import List
from bs4 import BeautifulSoup

from plugins.base_plugin import BasePlugin
from core.plugin_interface import SearchResult, ChapterInfo, BookStatus
from core.plugin_registry import PluginRegistry


class PluginBqg(BasePlugin):
    """Plugin for bqg655.cc (笔趣阁)"""

    DEFAULT_BASE_URL = "https://www.bqg655.cc"
    API_BASE_URL = "https://apibi.cc"

    def __init__(self, base_url: str = None, headless: bool = True, chrome_path: str = None):
        super().__init__()
        self._base_url = base_url or self.DEFAULT_BASE_URL
        self._headless = headless  # Stored but not used (HTTP mode doesn't need browser)
        self._chrome_path = chrome_path  # Stored but not used (HTTP mode doesn't need browser)

    @property
    def name(self) -> str:
        return "bqg"

    @property
    def domain(self) -> str:
        return self._base_url

    def search(self, keyword: str) -> List[SearchResult]:
        """Search for novels using the site's JSON API.

        GET https://www.bqg655.cc/api/search?q={书名}
        """
        results = []

        try:
            search_url = f"{self._base_url}/api/search?q={keyword}"

            # Use UTF-8 encoding for API response
            resp = self._session.get(search_url, timeout=self.REQUEST_TIMEOUT, verify=False)
            resp.encoding = 'utf-8'
            text = resp.text

            data = json.loads(text)
            if 'data' in data and isinstance(data['data'], list):
                for item in data['data']:
                    results.append(SearchResult(
                        title=item.get('title', ''),
                        author=item.get('author', '未知'),
                        status=BookStatus.UNKNOWN,
                        url=f"{self._base_url}/book/{item.get('id', '')}/",
                        plugin=self.name
                    ))

        except Exception as e:
            print(f"[bqg] Search failed: {e}")

        return results

    def get_chapter_list(self, book_url: str) -> List[ChapterInfo]:
        """Get chapter list using the API.

        First get book info to find total chapter count:
        GET https://apibi.cc/api/book?id={book_id}

        The response includes lastchapterid which is the total chapter count.
        """
        chapters = []

        try:
            # Extract book ID from URL like /book/1000/ or /book/1000
            book_id = self._extract_book_id(book_url)
            if not book_id:
                print(f"[bqg] Failed to extract book ID from: {book_url}")
                return chapters

            # Get book info to find total chapters
            book_info_url = f"{self.API_BASE_URL}/api/book?id={book_id}"
            resp = self._session.get(book_info_url, timeout=self.REQUEST_TIMEOUT, verify=False)
            resp.encoding = 'utf-8'
            data = json.loads(resp.text)

            total_chapters = int(data.get('lastchapterid', 0))
            book_title = data.get('title', '')

            # Create chapter list with sequential numbering
            for i in range(1, total_chapters + 1):
                chapters.append(ChapterInfo(
                    index=i,
                    title=f"第{i}章",  # Will be updated when fetching content
                    url=f"{self.API_BASE_URL}/api/chapter?id={book_id}&chapterid={i}"
                ))

        except Exception as e:
            print(f"[bqg] Failed to get chapter list: {e}")

        return chapters

    def get_chapter_content(self, chapter_url: str) -> tuple:
        """Get chapter content using the API.

        GET https://apibi.cc/api/chapter?id={book_id}&chapterid={chapter_num}

        Response:
        {
          "chaptername": "章节名",
          "txt": "章节正文"
        }

        Returns:
            tuple: (chaptername, content) - chapter name and cleaned content
        """
        content = ""
        chaptername = ""

        try:
            # Use the chapter URL directly (already formatted as API URL)
            resp = self._session.get(chapter_url, timeout=self.REQUEST_TIMEOUT, verify=False)
            resp.encoding = 'utf-8'
            data = json.loads(resp.text)

            chaptername = data.get('chaptername', '')
            content = data.get('txt', '')

            # Clean ad text
            content = self._clean_content(content)

        except Exception as e:
            print(f"[bqg] Failed to get chapter content: {e}")

        return chaptername, content

    def _extract_book_id(self, book_url: str) -> str:
        """Extract book ID from book URL.

        URLs can be:
        - https://www.bqg655.cc/book/1000/
        - https://www.bqgcp.cc/book/1000/
        - /book/1000/
        """
        import re
        match = re.search(r'/book/(\d+)/?', book_url)
        if match:
            return match.group(1)
        return ""

    def _clean_content(self, content: str) -> str:
        """Remove ad text from chapter content."""
        ad_keywords = [
            '请收藏本站：',
            '手机版：',
            '『点此报错』',
            '『加入书签』',
            '或者跳过本章点击下一章继续阅读',
        ]

        lines = content.split('\n')
        cleaned_lines = []

        for line in lines:
            is_ad = False
            for keyword in ad_keywords:
                if keyword in line:
                    is_ad = True
                    break
            if not is_ad:
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines).strip()


# Register plugin
PluginRegistry.get_instance().register(PluginBqg())


def create_instance(**kwargs) -> 'PluginBqg':
    """Create a new independent PluginBqg instance.

    Args:
        **kwargs: Arguments passed to PluginBqg constructor

    Returns:
        New PluginBqg instance
    """
    return PluginBqg(
        base_url=kwargs.get('base_url'),
        headless=kwargs.get('headless', True),
        chrome_path=kwargs.get('chrome_path')
    )