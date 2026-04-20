"""bqg plugin for novel downloader - 笔趣阁

Based on docs/coding-plan/bqg.md

Search uses JSON API, but chapter content requires Playwright due to
anti-bot verification that redirects to /userverify.
"""

import os
import sys
import time
import re
import requests
from typing import List
from bs4 import BeautifulSoup
from urllib.parse import quote

from plugins.base_plugin import BasePlugin
from core.plugin_interface import SearchResult, ChapterInfo, BookStatus
from core.plugin_registry import PluginRegistry


# Simple logger
class SimpleLogger:
    """Simple logger that prints to stdout/stderr."""

    def __init__(self, prefix: str = "[bqg]"):
        self.prefix = prefix

    def _format(self, level: str, msg: str) -> str:
        return f"{self.prefix} {level}: {msg}"

    def info(self, msg: str):
        print(self._format("INFO", msg), file=sys.stdout)

    def warning(self, msg: str):
        print(self._format("WARN", msg), file=sys.stdout)

    def error(self, msg: str):
        print(self._format("ERROR", msg), file=sys.stderr)


_logger = SimpleLogger()


class BrowserAutomationError(Exception):
    """Exception raised when browser automation fails."""
    pass


class PluginBqg(BasePlugin):
    """Plugin for bqgcp.cc (笔趣阁)"""

    BASE_URL = "https://www.bqgcp.cc"

    DEFAULT_CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    def __init__(self, chrome_path: str = None, headless: bool = False, slow_mo: int = 100):
        """Initialize the bqg plugin with browser settings."""
        self._chrome_path = chrome_path or self.DEFAULT_CHROME_PATH
        self._headless = headless
        self._slow_mo = slow_mo

        self._browser = None
        self._context = None
        self._page = None
        self._playwright = None

    @property
    def name(self) -> str:
        return "bqg"

    @property
    def domain(self) -> str:
        return self.BASE_URL

    def _ensure_browser(self) -> bool:
        """Ensure browser is connected and ready."""
        try:
            if self._browser is not None and self._page is not None and not self._page.is_closed():
                return True

            self._cleanup()

            import asyncio
            from playwright.sync_api import sync_playwright

            try:
                existing_loop = asyncio.get_event_loop()
                if existing_loop.is_running():
                    asyncio.set_event_loop(None)
                else:
                    existing_loop.close()
            except Exception:
                pass

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            _logger.info("Starting Playwright...")
            self._playwright = sync_playwright().start()

            _logger.info(f"Launching browser (headless={self._headless})...")
            self._browser = self._playwright.chromium.launch(
                headless=self._headless,
                slow_mo=self._slow_mo,
                args=['--start-maximized'],
                executable_path=self._chrome_path if os.path.exists(self._chrome_path) else None,
            )

            self._context = self._browser.new_context()
            self._page = self._context.new_page()
            _logger.info("Browser ready")
            return True

        except Exception as e:
            _logger.error(f"Failed to initialize browser: {e}")
            self._cleanup()
            return False

    def _cleanup(self):
        """Clean up browser resources."""
        try:
            if self._context:
                try:
                    self._context.close()
                except Exception:
                    pass
                self._context = None
        except Exception:
            pass

        try:
            if self._browser:
                try:
                    self._browser.close()
                except Exception:
                    pass
                self._browser = None
        except Exception:
            pass

        try:
            if self._playwright:
                try:
                    self._playwright.stop()
                except Exception:
                    pass
                self._playwright = None
        except Exception:
            pass

        self._page = None

    def close(self):
        """Close browser resources."""
        self._cleanup()

    def search(self, keyword: str) -> List[SearchResult]:
        """Search for novels on bqgcp.cc using JSON API.

        The search results are loaded dynamically via JavaScript, but we can
        directly access the JSON API endpoint.
        """
        results = []

        try:
            import json

            encoded_keyword = quote(keyword, safe='')

            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': f'{self.BASE_URL}/s?q={encoded_keyword}',
                'X-Requested-With': 'XMLHttpRequest',
            })

            json_url = f"{self.BASE_URL}/user/search.html?q={encoded_keyword}"
            json_response = session.get(json_url, timeout=10, verify=False)
            json_response.raise_for_status()

            data = json.loads(json_response.text)

            # API may return integer (1) or empty array when no results
            if not isinstance(data, list):
                _logger.warning(f"Search API returned {type(data).__name__} instead of list")
                return results

            for item in data:
                title = item.get('articlename', '')
                author = item.get('author', '未知')
                link = item.get('url_list', '')

                if link and not link.startswith('http'):
                    link = self.BASE_URL + link

                results.append(SearchResult(
                    title=title,
                    author=author,
                    status=BookStatus.UNKNOWN,
                    url=link,
                    plugin=self.name
                ))

        except Exception as e:
            _logger.error(f"Search failed: {e}")
            raise

        return results

    def get_chapter_list(self, book_url: str) -> List[ChapterInfo]:
        """Get chapter list for a book using HTTP."""
        chapters = []

        try:
            html = self.get_html_content(book_url)
            soup = BeautifulSoup(html, 'html.parser')

            # Find chapter list
            chapter_list = soup.select('.listmain dl dd a')
            for idx, a_tag in enumerate(chapter_list, start=1):
                chapter_title = a_tag.get('title', '') or a_tag.text.strip()
                chapter_url = a_tag.get('href', '')

                if not chapter_url:
                    continue

                if chapter_url and not chapter_url.startswith('http'):
                    chapter_url = self.BASE_URL + chapter_url

                # Extract chapter number from title (format: "1、" or "1、标题")
                chapter_index = idx
                match = re.search(r'^(\d+)、', chapter_title)
                if match:
                    chapter_index = int(match.group(1))

                chapters.append(ChapterInfo(
                    index=chapter_index,
                    title=chapter_title,
                    url=chapter_url
                ))

        except Exception as e:
            _logger.error(f"Failed to get chapter list: {e}")

        return chapters

    def get_chapter_content(self, chapter_url: str) -> str:
        """Get chapter content using browser automation.

        The chapter page has anti-bot verification that requires JavaScript.
        We use Playwright to navigate and wait for content to load.
        """
        content = ""

        try:
            if not self._ensure_browser():
                raise BrowserAutomationError("Failed to initialize browser")

            _logger.info(f"Getting chapter content from: {chapter_url}")

            self._page.goto(chapter_url, wait_until="load", timeout=30000)

            # Wait for content to load (page shows "加载中..." initially)
            max_wait = 15
            start_time = time.time()

            while time.time() - start_time < max_wait:
                # Try to get content using JavaScript (better encoding handling)
                try:
                    content_div = self._page.query_selector('#chaptercontent')
                    if content_div:
                        raw_text = content_div.inner_text()

                        # Check if content is meaningful (not just the "too short" message)
                        if raw_text and len(raw_text) > 20:
                            content = self._clean_content(raw_text)
                            if content:
                                break
                except Exception:
                    pass

                self._page.wait_for_timeout(500)

            # Fallback: try parsing HTML if JS method failed
            if not content:
                html_content = self._page.content()
                content = self._parse_chapter_content(html_content)

            _logger.info(f"Got chapter content, length: {len(content)}")

        except BrowserAutomationError:
            raise
        except Exception as e:
            _logger.error(f"Failed to get chapter content: {e}")

        return content

    def _parse_chapter_content(self, html: str) -> str:
        """Parse and clean chapter content from HTML.

        Content is in:
        <div id="chaptercontent" class="Readarea ReadAjax_content">
            ...paragraph text...
        </div>

        Note: The page may show "本章由于字数太少，暂不显示" for short chapters.
        """
        soup = BeautifulSoup(html, 'html.parser')

        content_div = soup.find('div', id='chaptercontent')
        if not content_div:
            return ""

        # Get all text content
        content_lines = []
        for elem in content_div.find_all(recursive=False):
            if elem.name == 'br':
                continue
            text = elem.get_text().strip()
            if text:
                content_lines.append(text)

        content = '\n'.join(content_lines)

        # Clean ad text
        content = self._clean_content(content)

        return content

    def _clean_content(self, content: str) -> str:
        """Remove ad text from chapter content.

        According to docs/coding-plan/bqg.md, need to remove:
        - Lines containing '请收藏本站：'
        - Lines containing '手机版：'
        """
        ad_keywords = [
            '请收藏本站：',
            '手机版：',
            '『点此报错』',
            '『加入书签』',
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

    def __del__(self):
        """Cleanup when object is destroyed."""
        self._cleanup()


# Register plugin
PluginRegistry.get_instance().register(PluginBqg())


def create_instance(**kwargs) -> 'PluginBqg':
    """Create a new independent PluginBqg instance.

    Each call creates a new instance with its own browser.
    This is used when downloading multiple novels simultaneously.

    Args:
        **kwargs: Arguments passed to PluginBqg constructor

    Returns:
        New PluginBqg instance
    """
    return PluginBqg(**kwargs)
