import requests
import re
import os
from collections import namedtuple

from bs4 import BeautifulSoup


Video = namedtuple('Video', ('title', 'url'))


class Playlist():
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

    _playlist_url_template = 'https://yewtu.be/playlist?list={list_id}&page={page}'
    _video_url_template = 'https://www.youtube.com{href}'
    _video_url_re = re.compile(r'<a style=\"width:100%\" href=\"(/watch\?v=[^&]+).*\"\>[^`]+?<p dir=\"auto\">(.*)</p>')


    def __init__(self, list_id_or_url:str):
        if 'list=' in list_id_or_url:
            self._list_id = re.search(r'list=([a-zA-Z0-9-_]+)', list_id_or_url).group(1)
        else:
            self._list_id = list_id_or_url

    def get_videos(self) -> list[Video]:
        '''
        get all videos from playlist

        Return:
            namedtuple('Video', ('title', 'url'))
        '''

        videos = []
        page = 1

        while 1:
            response = requests.get(self._playlist_url_template.format(
                list_id=self._list_id,
                page=page
            ))
            response.encoding = 'utf-8'
            if response.status_code != 200:
                raise ConnectionError(f'request to page={page} status_code={200}')
            html = response.text
            
            videos += self._fetch_videos_from_html(html)
            
            if self._is_next_page_exist(html):
                page += 1
            else:
                break

        return videos

    def _fetch_videos_from_html(self, html: str) -> list[Video]:
        videos = []
        for href, title in self._video_url_re.findall(html):
            url = self._video_url_template.format(href=href)
            videos.append(Video(title, url))
        return videos
    
    def _is_next_page_exist(self, html: str) -> bool:
        bs = BeautifulSoup(html, 'html.parser')
        next_page_div = bs.find('div', attrs={
            'class': 'pure-u-1 pure-u-lg-1-5',
            'style': 'text-align:right',
        })
        return next_page_div.a is not None