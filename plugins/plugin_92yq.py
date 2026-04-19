"""92yq plugin for novel downloader - 就爱言情小说网

Based on docs/coding-plan/92yq.md
"""

import re
from typing import List
from bs4 import BeautifulSoup

from plugins.base_plugin import BasePlugin
from core.plugin_interface import SearchResult, ChapterInfo, BookStatus
from core.plugin_registry import PluginRegistry


class Plugin92yq(BasePlugin):
    """Plugin for 92yanqing.com (就爱言情小说网)"""

    BASE_URL = "https://www.92yanqing.com"

    @property
    def name(self) -> str:
        return "92yq"

    @property
    def domain(self) -> str:
        return self.BASE_URL

    def search(self, keyword: str) -> List[SearchResult]:
        """Search for novels on 92yanqing.

        URL format: https://www.92yanqing.com/s/?searchkey={keyword}

        Search results are in:
        <div class="ranklist mt10">
            <div class="content">
                <dl>
                    <a href="/read/99989/" class="cover" title="...">
                    <dt><a href="/read/99989/" title="...">Title</a></dt>
                    <dd><a href="/author/...">Author</a><span>连载</span><span>字数</span></dd>
                    <dd>Description...</dd>
                </dl>
            </div>
        </div>
        """
        results = []
        search_url = f"{self.BASE_URL}/s/?searchkey={keyword}"

        try:
            html = self.get_html_content(search_url)
            soup = BeautifulSoup(html, 'html.parser')

            # Find all search result items
            content_div = soup.select('.ranklist .content dl')
            for item in content_div:
                # Get title and link from dt a
                dt_a = item.select_one('dt a')
                if not dt_a:
                    continue

                title = dt_a.get('title', '') or dt_a.text.strip()
                link = dt_a.get('href', '')
                if link and not link.startswith('http'):
                    link = self.BASE_URL + link

                # Get author from dd a
                author = "未知"
                status_text = ""
                dd_tags = item.select('dd')

                for dd in dd_tags:
                    # Check for author link (usually in second dd after dt)
                    author_link = dd.select_one('a')
                    if author_link and author == "未知":
                        href = author_link.get('href', '')
                        # Skip cover links, look for author links
                        if '/author/' in href:
                            author = author_link.text.strip()

                    # Check for spans with status
                    spans = dd.select('span')
                    for span in spans:
                        span_text = span.text.strip()
                        if span_text in ['连载', '完结']:
                            status_text = span_text
                            break

                results.append(SearchResult(
                    title=title,
                    author=author,
                    status=self.parse_status(status_text),
                    url=link,
                    plugin=self.name
                ))

        except Exception as e:
            print(f"[92yq] Search failed: {e}")
            raise

        return results

    def get_chapter_list(self, book_url: str) -> List[ChapterInfo]:
        """Get chapter list for a book.

        Chapter list is in:
        <div class="chapterlist mt10">
            <div class="all">
                <ul>
                    <li><a href="..." title="...">Chapter Title</a></li>
                </ul>
            </div>
        </div>
        """
        chapters = []

        try:
            html = self.get_html_content(book_url)
            soup = BeautifulSoup(html, 'html.parser')

            # Find chapter list
            chapter_list = soup.select('.chapterlist .all ul li a')
            for idx, li in enumerate(chapter_list, start=1):
                a_tag = li
                chapter_title = a_tag.get('title', '') or a_tag.text.strip()
                chapter_url = a_tag.get('href', '')

                if not chapter_url:
                    continue

                if chapter_url and not chapter_url.startswith('http'):
                    chapter_url = self.BASE_URL + chapter_url

                chapters.append(ChapterInfo(
                    index=idx,
                    title=chapter_title,
                    url=chapter_url
                ))

        except Exception as e:
            print(f"[92yq] Failed to get chapter list: {e}")

        return chapters

    def get_chapter_content(self, chapter_url: str) -> str:
        """Get chapter content.

        Content is in:
        <div class="read">
            <div class="content">
                <div id="booktxt">
                    <p>Paragraph 1</p>
                    <p>Paragraph 2</p>
                </div>
                <div class="report">...</div>
            </div>
        </div>

        Pagination: If there's a "下一页" link, follow it until "下一章" or "没有了".
        """
        content_parts = []

        try:
            current_url = chapter_url

            # Keep fetching pages until we reach end of chapter
            while current_url:
                html = self.get_html_content(current_url)
                soup = BeautifulSoup(html, 'html.parser')

                # Get content from #booktxt
                booktxt = soup.select_one('#booktxt')
                if booktxt:
                    paragraphs = booktxt.select('p')
                    for p in paragraphs:
                        text = p.get_text().strip()
                        if text:
                            content_parts.append(text)

                # Check for next page within chapter
                # Look for rel="next" link
                next_link = soup.select_one('a[rel="next"]')
                if next_link:
                    next_href = next_link.get('href', '')
                    next_text = next_link.get_text().strip()

                    # If it's "下一页" (next page), continue
                    # If it's "下一章" (next chapter) or "没有了" (none), stop
                    if '下一章' in next_text or '没有了' in next_text:
                        break
                    if next_href and not next_href.startswith('http'):
                        next_href = self.BASE_URL + next_href
                    current_url = next_href
                else:
                    break

        except Exception as e:
            print(f"[92yq] Failed to get chapter content: {e}")

        return '\n'.join(content_parts)


# Register plugin
PluginRegistry.get_instance().register(Plugin92yq())


def create_instance(**kwargs) -> 'Plugin92yq':
    """Create a new independent Plugin92yq instance.

    Each call creates a new instance with its own HTTP connection.
    This is used when downloading multiple novels simultaneously.

    Returns:
        New Plugin92yq instance
    """
    return Plugin92yq()
