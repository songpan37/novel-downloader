"""3yt plugin for novel downloader - using Playwright browser automation

Based on docs/coding-plan/3yt.md

The 3yt website requires JavaScript to render search results, so we use
Playwright for browser automation instead of simple HTTP requests.
"""

import os
import sys
import time
import re
from typing import List, Optional, Tuple

from bs4 import BeautifulSoup

from plugins.base_plugin import BasePlugin
from core.plugin_interface import SearchResult, ChapterInfo, BookStatus
from core.plugin_registry import PluginRegistry


# Simple logger that works without external dependencies
class SimpleLogger:
    """Simple logger that prints to stdout/stderr."""

    def __init__(self, prefix: str = "[3yt]"):
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


class Plugin3yt(BasePlugin):
    """Plugin for 3yt.org website using Playwright browser automation.

    This plugin handles the JavaScript-rendered pages on 3yt.org by using
    Playwright to automate browser interactions.
    """

    DEFAULT_BASE_URL = "https://www.3yt.org"
    DEFAULT_CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    def __init__(self, chrome_path: str = None, headless: bool = False, slow_mo: int = 100, base_url: str = None):
        """
        Initialize the 3yt plugin with browser settings.

        Args:
            chrome_path: Path to Chrome executable. If None, uses default path.
            headless: Run browser in headless mode.
            slow_mo: Slow down interactions by specified milliseconds.
            base_url: Base URL for the plugin. If None, uses default.
        """
        self._chrome_path = chrome_path or self.DEFAULT_CHROME_PATH
        self._headless = headless
        self._slow_mo = slow_mo
        self._base_url = base_url or self.DEFAULT_BASE_URL

        self._browser = None
        self._context = None
        self._page = None
        self._playwright = None

    @property
    def name(self) -> str:
        return "3yt"

    @property
    def domain(self) -> str:
        return self._base_url

    @property
    def SEARCH_URL(self) -> str:
        return self._base_url

    def _ensure_browser(self) -> bool:
        """Ensure browser is connected and ready.

        Returns:
            True if browser is ready, False otherwise.
        """
        try:
            # Check if browser already exists and is valid
            if self._browser is not None and self._page is not None and not self._page.is_closed():
                return True

            # Clean up any existing resources first
            self._cleanup()

            # Import Playwright
            import asyncio
            from playwright.sync_api import sync_playwright

            # Reset any existing event loop issues completely
            try:
                existing_loop = asyncio.get_event_loop()
                if existing_loop.is_running():
                    # If loop is running in another thread, we need to create a new one
                    asyncio.set_event_loop(None)
                else:
                    existing_loop.close()
            except Exception:
                pass

            # Create fresh event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Start Playwright
            _logger.info("Starting Playwright...")
            self._playwright = sync_playwright().start()

            # Launch browser
            _logger.info(f"Launching browser (headless={self._headless})...")
            self._browser = self._playwright.chromium.launch(
                headless=self._headless,
                slow_mo=self._slow_mo,
                args=['--start-maximized'],
                executable_path=self._chrome_path if os.path.exists(self._chrome_path) else None,
            )

            # Create context and page
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
        """Close browser resources. Call this when done with the plugin."""
        self._cleanup()

    def search(self, keyword: str) -> List[SearchResult]:
        """Search for novels on 3yt using browser automation.

        According to docs/coding-plan/3yt.md:
        1. Navigate to https://www.3yt.org/
        2. Fill in the search box with class "search" and id "bdcsMain"
        3. Click the search button with class "searchBtn"
        4. The search results appear in a popup window with URL like /search/94/1.html
        5. Parse results from #sitembox dl structure

        Args:
            keyword: Search keyword (book name or author)

        Returns:
            List of SearchResult objects
        """
        results = []
        original_page = self._page
        popup_page = None

        try:
            if not self._ensure_browser():
                raise BrowserAutomationError("Failed to initialize browser")

            _logger.info(f"Searching for: {keyword}")

            # Navigate to main page - use commit to avoid timeout on slow sites
            _logger.info(f"Navigating to {self.SEARCH_URL}...")
            try:
                self._page.goto(self.SEARCH_URL, wait_until="commit", timeout=30000)
            except Exception as e:
                _logger.warning(f"Navigation with 'commit' failed: {e}, trying 'domcontentloaded'...")
                self._page.goto(self.SEARCH_URL, wait_until="domcontentloaded", timeout=30000)
            self._page.wait_for_timeout(2000)  # Wait for page to stabilize

            # Fill in search box - use fill() which clears and fills
            _logger.info("Filling search box...")
            search_input = self._page.wait_for_selector(
                'input.search#bdcsMain[name="searchkey"]',
                timeout=10000
            )
            search_input.fill(keyword)  # fill() clears and fills in one step
            _logger.info(f"Search term entered: {keyword}")

            # Wait a moment for the input to be processed
            self._page.wait_for_timeout(300)

            # Click search button
            _logger.info("Clicking search button...")
            search_btn = self._page.wait_for_selector(
                'input.searchBtn[type="submit"][value="搜索"]',
                timeout=5000
            )
            search_btn.click()

            # Wait for popup window to appear - the search opens in a new window
            _logger.info("Waiting for search results popup...")

            # Wait up to 10 seconds for a new page to appear
            max_wait = 10
            start_time = time.time()
            initial_page_count = len(self._context.pages)

            while time.time() - start_time < max_wait:
                self._page.wait_for_timeout(500)
                if len(self._context.pages) > initial_page_count:
                    # New page appeared - this is the popup
                    popup_page = self._context.pages[-1]
                    _logger.info(f"Popup appeared with URL: {popup_page.url}")
                    break

                # Also check if URL changed on current page
                current_url = self._page.url
                if '/search/' in current_url:
                    _logger.info(f"URL changed to search page: {current_url}")
                    popup_page = self._page
                    break

            # If popup found, switch to it
            if popup_page and popup_page != original_page:
                self._page = popup_page
                # Wait for the popup page to load
                self._page.wait_for_load_state("load", timeout=15000)
                self._page.wait_for_timeout(1000)

            # Also check if we got redirected on the original page
            elif '/search/' in self._page.url:
                _logger.info(f"Redirected to: {self._page.url}")

            # If still on main page, try waiting more for popup
            if self._page.url == self.SEARCH_URL or self._page.url == self.SEARCH_URL + '/':
                _logger.info("Still on main page, waiting more...")
                self._page.wait_for_timeout(3000)
                if len(self._context.pages) > initial_page_count:
                    popup_page = self._context.pages[-1]
                    self._page = popup_page

            _logger.info(f"Final page URL: {self._page.url}")

            # Parse the search results
            html_content = self._page.content()
            results = self._parse_search_results(html_content)

            _logger.info(f"Found {len(results)} results")

        except BrowserAutomationError:
            raise
        except Exception as e:
            _logger.error(f"Search failed: {e}")
            import traceback
            traceback.print_exc()
            raise BrowserAutomationError(f"Search failed: {e}")

        finally:
            # Close popup if it was opened and switch back to original page
            if popup_page and popup_page != original_page:
                try:
                    popup_page.close()
                except Exception:
                    pass
                self._page = original_page

            # Close browser after search
            self._cleanup()

        return results

    def _parse_search_results(self, html: str) -> List[SearchResult]:
        """Parse search results from HTML content.

        According to docs/coding-plan/3yt.md, the search results are in:
        <div id="sitembox">
            <dl>
                <dt><a href="/ml/213930/"><img src="..." alt="..."></a></dt>
                <dd><h3><a href="/ml/213930/">Title</a></h3></dd>
                <dd class="book_other">作者：<span>Author</span>状态：<span>Status</span>...</dd>
                <dd class="book_des">Description</dd>
                <dd class="book_other">最新章节：<a href="...">Chapter</a> 更新时间：<span>Date</span></dd>
            </dl>
        </div>
        """
        results = []
        soup = BeautifulSoup(html, 'html.parser')

        sitembox = soup.select('#sitembox dl')
        for item in sitembox:
            try:
                # Get title from dd h3 a
                title_elem = item.select_one('dd h3 a')
                if not title_elem:
                    continue
                title = title_elem.text.strip()

                # Get link
                link = title_elem.get('href', '')
                if link and not link.startswith('http'):
                    link = self._base_url + link

                # Get author, status from dd.book_other
                book_other = item.select_one('dd.book_other')
                author = "未知"
                status_text = ""
                description = ""

                if book_other:
                    spans = book_other.find_all('span')
                    if len(spans) >= 1:
                        author = spans[0].text.strip()
                    if len(spans) >= 2:
                        status_text = spans[1].text.strip()

                # Get description from dd.book_des
                desc_elem = item.select_one('dd.book_des')
                if desc_elem:
                    description = desc_elem.text.strip()

                results.append(SearchResult(
                    title=title,
                    author=author,
                    status=self.parse_status(status_text),
                    url=link,
                    plugin=self.name
                ))
            except Exception as e:
                _logger.warning(f"Failed to parse search result item: {e}")
                continue

        return results

    def get_chapter_list(self, book_url: str) -> List[ChapterInfo]:
        """Get chapter list for a book using browser automation.

        According to docs/coding-plan/3yt.md:
        1. Navigate to book URL like https://www.3yt.org/ml/213930/
        2. Find <div id="list"> containing chapter list
        3. Skip <dt> tags (headers), start from last <dt> (which contains "正文" header)
        4. Get all <dd> tags after the "正文" <dt>
        """
        chapters = []

        try:
            if not self._ensure_browser():
                raise BrowserAutomationError("Failed to initialize browser")

            _logger.info(f"Getting chapter list from: {book_url}")

            # Navigate to book page
            self._page.goto(book_url, wait_until="load", timeout=30000)
            self._page.wait_for_timeout(1000)

            # Get page content
            html_content = self._page.content()
            chapters = self._parse_chapter_list(html_content, book_url)

            _logger.info(f"Found {len(chapters)} chapters")

        except BrowserAutomationError:
            raise
        except Exception as e:
            _logger.error(f"Failed to get chapter list: {e}")
            import traceback
            traceback.print_exc()

        return chapters

    def _parse_chapter_list(self, html: str, base_url: str = "") -> List[ChapterInfo]:
        """Parse chapter list from HTML content.

        The chapter list is in:
        <div id="list">
            <dl>
                <dt>...提示信息...</dt>
                <dd><a href="/ml/213930/151017439.html">章节标题</a></dd>
                ...
                <dt><b>《书名》正文</b><a href="...">下载链接</a></dt>
                <dd><a href="/ml/213930/102812715.html">第1章 标题</a></dd>
                <dd><a href="/ml/213930/102812717.html">第2章 标题</a></dd>
                ...
            </dl>
        </div>

        We need to skip the first <dt> and start from the "正文" section.
        """
        chapters = []
        soup = BeautifulSoup(html, 'html.parser')

        list_div = soup.find('div', id='list')
        if not list_div:
            _logger.warning("No #list div found")
            return chapters

        # Find all dl tags within list
        dls = list_div.find_all('dl')

        for dl in dls:
            dt_tags = dl.find_all('dt')
            dd_tags = dl.find_all('dd')

            # Look for the dl that contains "正文" in its dt
            has_main_content = False
            for dt in dt_tags:
                dt_text = dt.get_text()
                if '正文' in dt_text:
                    has_main_content = True
                    break

            if has_main_content:
                # Find the last dt position in this dl
                last_dt_index = -1
                all_elements = dl.find_all(['dt', 'dd'])
                for idx, elem in enumerate(all_elements):
                    if elem.name == 'dt':
                        last_dt_index = idx

                # Parse only dd tags after the last dt - sequential numbering
                chapter_idx = 1
                for elem in all_elements[last_dt_index + 1:]:
                    if elem.name == 'dd':
                        a_tag = elem.find('a')
                        if not a_tag:
                            continue

                        chapter_title = a_tag.text.strip()
                        chapter_url = a_tag.get('href', '')

                        if not chapter_url:
                            continue

                        if chapter_url and not chapter_url.startswith('http'):
                            chapter_url = self._base_url + chapter_url

                        chapters.append(ChapterInfo(
                            index=chapter_idx,
                            title=chapter_title,
                            url=chapter_url
                        ))
                        chapter_idx += 1

        return chapters

    def get_chapter_content(self, chapter_url: str) -> str:
        """Get chapter content using browser automation.

        According to docs/coding-plan/3yt.md:
        1. Navigate to chapter URL
        2. Find <div id="content"> with chapter text
        3. Clean up ads containing 'www.suyingwang.net' or '三月天更新速度全网最快'
        """
        content = ""

        try:
            if not self._ensure_browser():
                raise BrowserAutomationError("Failed to initialize browser")

            _logger.info(f"Getting chapter content from: {chapter_url}")

            # Navigate to chapter page
            self._page.goto(chapter_url, wait_until="load", timeout=30000)
            self._page.wait_for_timeout(500)

            # Get page content
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

        The chapter content is in:
        <div id="content" style="font-size: 24px;">
            <p>Paragraph text...</p>
            ...
        </div>

        Need to remove ads containing:
        - 'www.suyingwang.net'
        - '三月天更新速度全网最快'
        """
        soup = BeautifulSoup(html, 'html.parser')

        content_div = soup.find('div', id='content')
        if not content_div:
            return ""

        # Get all p tags and join their text
        paragraphs = content_div.find_all('p')
        content_lines = []

        for p in paragraphs:
            text = p.get_text().strip()
            if text:
                content_lines.append(text)

        content = '\n'.join(content_lines)

        # Clean up ad text
        content = self._clean_content(content)

        return content

    def _clean_content(self, content: str) -> str:
        """Remove ad text from chapter content.

        According to docs/coding-plan/3yt.md, need to remove:
        - Lines containing 'www.suyingwang.net'
        - Lines containing '三月天更新速度全网最快'
        """
        ad_keywords = [
            'www.suyingwang.net',
            '三月天更新速度全网最快',
            '更新速度全网最快',
            '请您少输字也别输错字',
            '可搜书名和作者'
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


# Global plugin instance for reuse
_global_plugin_instance = None


def get_plugin_instance(chrome_path: str = None, headless: bool = False, slow_mo: int = 100) -> 'Plugin3yt':
    """Get or create a global plugin instance.

    This allows reusing the browser instance across multiple operations.

    Args:
        chrome_path: Path to Chrome executable
        headless: Run browser in headless mode
        slow_mo: Slow down interactions

    Returns:
        Plugin3yt instance
    """
    global _global_plugin_instance

    if _global_plugin_instance is None:
        _global_plugin_instance = Plugin3yt(
            chrome_path=chrome_path,
            headless=headless,
            slow_mo=slow_mo
        )

    return _global_plugin_instance


def close_plugin():
    """Close the global plugin instance and cleanup browser resources."""
    global _global_plugin_instance

    if _global_plugin_instance is not None:
        _global_plugin_instance.close()
        _global_plugin_instance = None


# Register plugin
# Note: Plugin is registered but uses browser automation for operations
# The browser will be initialized lazily on first use
PluginRegistry.get_instance().register(Plugin3yt())


def create_instance(**kwargs) -> 'Plugin3yt':
    """Create a new independent Plugin3yt instance.

    Each call creates a new instance with its own browser.
    This is used when downloading multiple novels simultaneously.

    Args:
        **kwargs: Arguments passed to Plugin3yt constructor

    Returns:
        New Plugin3yt instance
    """
    return Plugin3yt(
        chrome_path=kwargs.get('chrome_path'),
        headless=kwargs.get('headless', False),
        slow_mo=kwargs.get('slow_mo', 100),
        base_url=kwargs.get('base_url')
    )
