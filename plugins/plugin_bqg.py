"""bqg plugin for novel downloader - 笔趣阁

Based on docs/coding-plan/bqg.md
"""

import re
from typing import List
from bs4 import BeautifulSoup

from plugins.base_plugin import BasePlugin
from core.plugin_interface import SearchResult, ChapterInfo, BookStatus
from core.plugin_registry import PluginRegistry


class PluginBqg(BasePlugin):
    """Plugin for bqgcp.cc (笔趣阁)"""

    BASE_URL = "https://www.bqgcp.cc"

    @property
    def name(self) -> str:
        return "bqg"

    @property
    def domain(self) -> str:
        return self.BASE_URL

    def search(self, keyword: str) -> List[SearchResult]:
        """Search for novels on bqgcp.cc.

        URL format: https://www.bqgcp.cc/s?q={keyword}

        Search results are in:
        <div class="so_list bookcase">
            <div class="type_show">
                <div class="bookbox">
                    <div class="box">
                        <div class="bookimg"><a href="/book/1000/"><img src="..."></a></div>
                        <div class="bookinfo">
                            <h4 class="bookname"><a href="/book/1000/">Title</a></h4>
                            <div class="author">作者：Author</div>
                            <div class="uptime">Description...</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        results = []
        search_url = f"{self.BASE_URL}/s?q={keyword}"

        try:
            html = self.get_html_content(search_url)
            soup = BeautifulSoup(html, 'html.parser')

            # Find all search result items
            bookboxes = soup.select('.so_list.bookcase .type_show .bookbox')
            for item in bookboxes:
                # Get title and link from h4.bookname a
                title_elem = item.select_one('.bookinfo h4.bookname a')
                if not title_elem:
                    continue

                title = title_elem.get('title', '') or title_elem.text.strip()
                link = title_elem.get('href', '')
                if link and not link.startswith('http'):
                    link = self.BASE_URL + link

                # Get author from div.author
                author = "未知"
                author_elem = item.select_one('.bookinfo .author')
                if author_elem:
                    author_text = author_elem.text.strip()
                    # Extract author name after "作者："
                    match = re.search(r'作者：(.+)', author_text)
                    if match:
                        author = match.group(1).strip()

                # Get description from div.uptime
                desc = ""
                desc_elem = item.select_one('.bookinfo .uptime')
                if desc_elem:
                    desc = desc_elem.text.strip()

                results.append(SearchResult(
                    title=title,
                    author=author,
                    status=BookStatus.UNKNOWN,  # bqg doesn't show status in search
                    url=link,
                    plugin=self.name
                ))

        except Exception as e:
            print(f"[bqg] Search failed: {e}")
            raise

        return results

    def get_chapter_list(self, book_url: str) -> List[ChapterInfo]:
        """Get chapter list for a book.

        Chapter list is in:
        <div class="listmain">
            <dl>
                <dt>Title最新章节列表</dt>
                <dd><a href="/book/1000/1.html">1、想等的人</a></dd>
                <dd><a href="/book/1000/2.html">2、倒计时</a></dd>
            </dl>
        </div>
        """
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
            print(f"[bqg] Failed to get chapter list: {e}")

        return chapters

    def get_chapter_content(self, chapter_url: str) -> str:
        """Get chapter content.

        Content is in:
        <div id="chaptercontent" class="Readarea ReadAjax_content">
            ...paragraph text...
            请收藏本站：https://www.bqg78.com
            手机版：https://m.bqg78.com
        </div>
        """
        content_parts = []

        try:
            html = self.get_html_content(chapter_url)
            soup = BeautifulSoup(html, 'html.parser')

            # Get content from #chaptercontent
            content_div = soup.select_one('#chaptercontent')
            if content_div:
                # Get text, handling <br> tags by replacing with newlines
                for elem in content_div.find_all(recursive=False):
                    if elem.name == 'br':
                        content_parts.append('\n')
                    else:
                        text = elem.get_text().strip()
                        if text:
                            content_parts.append(text)

                # If no direct children, get all text
                if not content_parts:
                    text = content_div.get_text(separator='\n', strip=True)
                    content_parts = text.split('\n')

            # Join and clean
            content = '\n'.join(content_parts)
            content = self._clean_content(content)

        except Exception as e:
            print(f"[bqg] Failed to get chapter content: {e}")

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

    Each call creates a new instance with its own HTTP connection.
    This is used when downloading multiple novels simultaneously.

    Returns:
        New PluginBqg instance
    """
    return PluginBqg()
