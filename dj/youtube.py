import requests
import re
import os
from collections import namedtuple


# YouTube Data API v3
# https://developers.google.com/youtube/registering_an_application
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', None)

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
        >>> y.videos
        [Video(title='Some video 1', url='https://www.youtube.com/watch?v=1111'),
         Video(title='Some video 2', url='https://www.youtube.com/watch?v=2222')]
    """

    _max_results_in_request = 50
    _api_url_template = 'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults={max_results}&pageToken={next_page_token}&playlistId={list_id}&key={key}'
    _video_url_template = 'https://www.youtube.com/watch?v=%s'


    def __init__(self, list_id_or_url:str):
        if 'list=' in list_id_or_url:
            self._list_id = re.search(r'list=([a-zA-Z0-9-_]+)', list_id_or_url).group(1)
        else:
            self._list_id = list_id_or_url

        if GOOGLE_API_KEY is None:
            raise ValueError(
                'GOOGLE_API_KEY is None, but shoud be a string. Maybe your forget to set env variable?!'
            )
        

    @property
    def videos(self):
        '''
        get all videos from playlist

        Return:
            namedtuple('Video', ('title', 'url'))
        '''

        videos = []
        next_page_token = ''

        while 1:
            response = self._send_request(next_page_token)
            
            jsn = response.json()
            videos += self._fetch_videos_from_json(jsn)
            
            if 'nextPageToken' not in jsn:
                break
            else:
                next_page_token = jsn['nextPageToken']

        return videos

    def _send_request(self, next_page_token: str=''):
        return requests.get(
            self._api_url_template.format(
                max_results=self._max_results_in_request,
                next_page_token=next_page_token,
                list_id=self._list_id,
                key=GOOGLE_API_KEY
            )
        )

    def _fetch_videos_from_json(self, jsn: dict):
        videos = []
        items = jsn['items']
        for item in items:
            video_id = item['snippet']['resourceId']['videoId']
            url = self._video_url_template % video_id
            title = item['snippet']['title']
            video = Video(title, url)
            videos.append(video)
        return videos