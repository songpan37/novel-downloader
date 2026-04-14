"""Base plugin implementation with common functionality"""

import requests
from bs4 import BeautifulSoup
from time import sleep
from typing import List

from core.plugin_interface import NovelPlugin, SearchResult, ChapterInfo, BookStatus


class BasePlugin(NovelPlugin):
    """Base class for novel plugins with common utilities"""

    MAX_RETRIES = 3
    RETRY_DELAY = 2
    REQUEST_TIMEOUT = 30

    def get_html_content(self, url: str) -> str:
        """Fetch HTML content with retry logic"""
        for retry in range(self.MAX_RETRIES):
            try:
                response = requests.get(url, timeout=self.REQUEST_TIMEOUT)
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
