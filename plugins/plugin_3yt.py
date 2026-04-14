"""3yt plugin for novel downloader - based on docs/coding-plan/3yt.md"""

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
            soup = BeautifulSoup(html, 'html.parser')

            # Parse search results from #sitembox dl structure
            sitembox = soup.select('#sitembox dl')
            for item in sitembox:
                # Get title from dd h3 a
                title_elem = item.select_one('dd h3 a')
                if not title_elem:
                    continue
                title = title_elem.text.strip()

                # Get link
                link = title_elem.get('href', '')
                if link and not link.startswith('http'):
                    link = self.domain + link

                # Get author, status from dd.book_other
                book_other = item.select_one('dd.book_other')
                author = "未知"
                status_text = ""

                if book_other:
                    spans = book_other.find_all('span')
                    if len(spans) >= 1:
                        author = spans[0].text.strip()
                    if len(spans) >= 2:
                        status_text = spans[1].text.strip()

                results.append(SearchResult(
                    title=title,
                    author=author,
                    status=self.parse_status(status_text),
                    url=link,
                    plugin=self.name
                ))
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise  # Re-raise so the caller knows search failed

        return results

    def get_chapter_list(self, book_url: str) -> List[ChapterInfo]:
        """Get chapter list for a book"""
        chapters = []

        try:
            html = self.get_html_content(book_url)
            soup = BeautifulSoup(html, 'html.parser')

            # Find the list container
            list_div = soup.find('div', id='list')
            if not list_div:
                return chapters

            # Find all dt and dd tags
            dt_tags = list_div.select('dt')
            dd_tags = list_div.select('dd')

            # Skip chapters before the last <dt> (which contains "正文" header)
            # The last <dt> contains the "正文" section marker
            if len(dt_tags) >= 1:
                # Find the index of the last dt that has "正文" or similar marker
                last_dt_index = -1
                for i, dt in enumerate(dt_tags):
                    dt_text = dt.get_text()
                    if '正文' in dt_text or '正文卷' in dt_text:
                        last_dt_index = i

                # Only keep dd tags after the last "正文" dt
                if last_dt_index >= 0 and last_dt_index < len(dt_tags) - 1:
                    # Get dds that come after the "正文" dt
                    all_dls = list_div.find_all('dl')
                    for dl in all_dls:
                        dl_dts = dl.find_all('dt')
                        dl_dds = dl.find_all('dd')
                        if any('正文' in dt.get_text() for dt in dl_dts):
                            # This dl contains "正文", use its dds
                            dd_tags = dl_dds
                            break
            else:
                # Fallback: use all dd tags
                dd_tags = list_div.select('dd')

            chapter_index = 1
            for dd in dd_tags:
                a_tag = dd.find('a')
                if not a_tag:
                    continue

                chapter_title = a_tag.text.strip()
                chapter_url = a_tag.get('href', '')

                if not chapter_url:
                    continue

                if chapter_url and not chapter_url.startswith('http'):
                    chapter_url = self.domain + chapter_url

                # Extract chapter number from title
                match = re.search(r'第(\d+)章', chapter_title)
                if match:
                    chapter_index = int(match.group(1))

                chapters.append(ChapterInfo(
                    index=chapter_index,
                    title=chapter_title,
                    url=chapter_url
                ))
                chapter_index += 1

        except Exception as e:
            pass

        return chapters

    def get_chapter_content(self, chapter_url: str) -> str:
        """Get chapter content - cleaned text"""
        try:
            html = self.get_html_content(chapter_url)
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

        except Exception as e:
            return ""

    def _clean_content(self, content: str) -> str:
        """Remove ad text from chapter content"""
        # Remove lines containing ad keywords
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


# Register plugin
PluginRegistry.get_instance().register(Plugin3yt())
