"""3yt plugin for novel downloader"""

from typing import List
from bs4 import BeautifulSoup
import re

from plugins.base_plugin import BasePlugin
from core.plugin_interface import SearchResult, ChapterInfo, BookStatus
from core.plugin_registry import PluginRegistry


class Plugin3yt(BasePlugin):
    """Plugin for 3yt.org website"""

    @property
    def name(self) -> str:
        return "3yt"

    @property
    def domain(self) -> str:
        return "https://www.3yt.org"

    def search(self, keyword: str) -> List[SearchResult]:
        """Search for novels on 3yt"""
        results = []
        search_url = f"{self.domain}/search/?searchkey={keyword}"

        try:
            html = self.get_html_content(search_url)
            soup = self.parse_html(html)

            # Parse search results - adjust selectors based on actual site structure
            for item in soup.select('.book-list li, .novel-item, .search-result'):
                title_elem = item.select_one('.book-title, .title, h3')
                author_elem = item.select_one('.author, .book-author')
                status_elem = item.select_one('.status, .book-status')
                link_elem = item.select_one('a')

                if title_elem and link_elem:
                    title = title_elem.text.strip()
                    author = author_elem.text.strip() if author_elem else "未知"
                    status_text = status_elem.text.strip() if status_elem else ""
                    url = link_elem.get('href', '')
                    if url and not url.startswith('http'):
                        url = self.domain + url

                    results.append(SearchResult(
                        title=title,
                        author=author,
                        status=self.parse_status(status_text),
                        url=url,
                        plugin=self.name
                    ))
        except Exception as e:
            pass  # Return empty results on error

        return results

    def get_chapter_list(self, book_url: str) -> List[ChapterInfo]:
        """Get chapter list for a book"""
        chapters = []

        try:
            html = self.get_html_content(book_url)
            soup = self.parse_html(html)

            # Parse chapter list - adjust selectors based on actual site structure
            # Typically in #list dt/dd structure
            dt_tags = soup.select('#list dt')
            start_idx = 1
            if len(dt_tags) >= 2:
                start_idx = 1  # Skip category headers

            dd_tags = soup.select('#list dd')
            for idx, dd in enumerate(dd_tags):
                a_tag = dd.find('a')
                if a_tag and a_tag.text:
                    chapter_title = a_tag.text.strip()
                    chapter_url = a_tag.get('href', '')
                    if chapter_url and not chapter_url.startswith('http'):
                        chapter_url = self.domain + chapter_url

                    # Extract chapter number from title
                    chapter_index = idx + 1
                    match = re.search(r'第(\d+)章', chapter_title)
                    if match:
                        chapter_index = int(match.group(1))

                    chapters.append(ChapterInfo(
                        index=chapter_index,
                        title=chapter_title,
                        url=chapter_url
                    ))
        except Exception as e:
            pass  # Return empty list on error

        return chapters

    def get_chapter_content(self, chapter_url: str) -> str:
        """Get chapter content"""
        try:
            html = self.get_html_content(chapter_url)
            soup = self.parse_html(html)

            content_div = soup.find('div', id='content')
            if content_div:
                p_tags = content_div.find_all('p')
                content = '\n'.join([p.get_text() for p in p_tags])
                return content

            # Alternative structure
            content_div = soup.find('div', class_='content')
            if content_div:
                return content_div.get_text(separator='\n', strip=True)

        except Exception as e:
            pass

        return ""


# Register plugin
PluginRegistry.get_instance().register(Plugin3yt())
