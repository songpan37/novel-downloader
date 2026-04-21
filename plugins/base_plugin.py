"""Base plugin implementation with common functionality"""

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup
from time import sleep
from typing import List

# Suppress InsecureRequestWarning for all requests using verify=False
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from core.plugin_interface import NovelPlugin, SearchResult, ChapterInfo, BookStatus


class BasePlugin(NovelPlugin):
    """Base class for novel plugins with common utilities"""

    MAX_RETRIES = 3
    RETRY_DELAY = 2
    REQUEST_TIMEOUT = 30

    def __init__(self):
        super().__init__()
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        })

    def get_html_content(self, url: str) -> str:
        """Fetch HTML content with retry logic"""
        for retry in range(self.MAX_RETRIES):
            try:
                response = self._session.get(url, timeout=self.REQUEST_TIMEOUT, verify=False)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                if retry < self.MAX_RETRIES - 1:
                    sleep(self.RETRY_DELAY)
                else:
                    raise
        return ""

    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML with BeautifulSoup"""
        return BeautifulSoup(html, 'html.parser')

    def parse_status(self, status_text: str) -> BookStatus:
        """Parse status string to BookStatus enum"""
        if not status_text:
            return BookStatus.UNKNOWN
        status_text = status_text.strip().lower()
        if any(keyword in status_text for keyword in ['完结', '已完成', 'finished', 'completed']):
            return BookStatus.COMPLETED
        elif any(keyword in status_text for keyword in ['连载', '更新', 'serializing', 'ongoing']):
            return BookStatus.SERIALIZING
        return BookStatus.UNKNOWN
