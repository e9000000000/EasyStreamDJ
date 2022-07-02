import re
from collections import namedtuple

import aiohttp
from bs4 import BeautifulSoup


PlaylistSearchResult = namedtuple("PlaylistSearchResult", ("name", "url", "videos_amount"))
Video = namedtuple("Video", ("title", "url"))


class Playlist:
    """
    class to work with youtube playlist

    Args:
        list_id_or_url: str - youtube playlist id or url with playlist id
        for example https://www.youtube.com/playlist?list=AAA_AAAAAA-AAAAAAA is url
        AAA_AAAAAA-AAAAAAA is playlist id

    Examples:
        >>> y = Playlist('LISTID')
        >>> y.get_videos()
        [Video(title='Some video 1', url='https://www.youtube.com/watch?v=1111'),
         Video(title='Some video 2', url='https://www.youtube.com/watch?v=2222')]
    """

    _playlist_search_url_template = (
        "https://yewtu.be/search?q={text} content_type%3Aplaylist"
    )
    _playlist_url_template = "https://yewtu.be/playlist?list={list_id}&page={page}"
    _video_url_template = "https://www.youtube.com{href}"
    _video_from_playlist_re = re.compile(
        r"<a style=\"width:100%\" href=\"(/watch\?v=[^&]+).*\"\>[^`]+?<p dir=\"auto\">(.*)</p>"
    )
    _video_from_mix_re = re.compile(r"<a href=(\"\/watch\?v=[^&]+)[^`]+?<p dir=\"auto\">(.+)<\/p>")

    def __init__(self, list_id_or_url: str):
        if "list=" in list_id_or_url:
            regex_result = re.search(r"list=([a-zA-Z0-9-_]+)", list_id_or_url)
            if regex_result is None:
                raise ValueError(f"invalid argument {list_id_or_url=}")
            self._list_id = regex_result.group(1)
        else:
            self._list_id = list_id_or_url

    @staticmethod
    async def search(text: str) -> list[PlaylistSearchResult]:
        """search for a youtube playlists and return list of them"""

        url = Playlist._playlist_search_url_template.format(text=text)
        async with aiohttp.request("GET", url) as response:
            if response.status // 100 != 2:
                raise ConnectionError(f"search {response.status=} {url=}")
            html = await response.text()
            bs = BeautifulSoup(html, "html.parser")
            divs = bs.find_all(
                "div",
                attrs={
                    "class": "pure-u-1 pure-u-md-1-4",
                },
            )

        results = []
        for div in divs:
            a = div.div.a
            url = a.attrs["href"]
            p_amount, p_name = a.find_all("p")
            amount = int(p_amount.text.split()[0])
            name = p_name.text
            results.append(
                PlaylistSearchResult(
                    name = name,
                    url = url,
                    videos_amount = amount,
                )
            )
        return results

    async def get_videos(self) -> list[Video]:
        """get all videos from playlist"""

        videos = set()
        page = 1

        while True:
            url = self._playlist_url_template.format(list_id=self._list_id, page=page)
            async with aiohttp.request("GET", url) as response:
                if response.status != 200:
                    raise ConnectionError(
                        f"request to {page=} {response.status=} {url=}"
                    )
                html = await response.text()

                videos.update(self._fetch_videos_from_html(html))

                if self._is_next_page_exist(html):
                    page += 1
                else:
                    break

        return list(videos)

    def _fetch_videos_from_html(self, html: str) -> set[Video]:
        videos = set()
        for href, title in self._video_from_playlist_re.findall(html):
            url = self._video_url_template.format(href=href)
            videos.add(Video(title, url))
        if not videos:
            for href, title in self._video_from_mix_re.findall(html):
                url = self._video_url_template.format(href=href)
                videos.add(Video(title, url))
        return videos

    def _is_next_page_exist(self, html: str) -> bool:
        bs = BeautifulSoup(html, "html.parser")
        next_page_div = bs.find(
            "div",
            attrs={
                "class": "pure-u-1 pure-u-lg-1-5",
                "style": "text-align:right",
            },
        )
        return getattr(next_page_div, "a", None) is not None
