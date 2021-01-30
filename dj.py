#!/bin/python3

import requests
import json
import threading
import names
import re
import os
import sys
from pathlib import Path
from time import sleep
from collections import namedtuple


Video = namedtuple('Video', ('title', 'url'))

class StreamDj():
    """
    class to work with streamdj.ru

    Args:
        channel_name: str - nickname of streamdj user 
        for example https://streamdj.ru/c/e6000000000 is url e6000000000 is channel name

        author_name: str - name that will shows as a sender of music
        if leave it `None` it will generates by names lib. generated names looks like `Victor Owens` `Regina Franks`

    Examples:
        >>> s = StreamDj('someone')
        >>> s.send('https://www.youtube.com/watch?v=POb02mjj2zE')
        {'success': 1}
    """
    def __init__(self, channel_name:str, author_name:str=None):
        self._channel_name = channel_name
        self._custom_author_name = author_name

        self._channel_id = None
        self._base_main_dj_url = 'https://streamdj.ru/c/%s'
        self._base_post_url = 'https://streamdj.ru/includes/back.php?func=add_track&channel=%s'

    
    @property
    def _author_name(self):
        if self._custom_author_name is not None:
            return self._custom_author_name
        return names.get_full_name()

    def _update_channel_id(self):
        responce = requests.get(self._base_main_dj_url % self._channel_name)
        if responce.status_code != 200:
            raise ConnectionError(f'status_code={responce.status_code}')
        result = re.search(r'onclick=\"add_track\(([0-9]+)\)\"', responce.text)
        if result is None:
            raise ValueError(f'cant find channel id. channel_name={self._channel_name}') 
        self._channel_id = result.group(1)

    def send(self, video_url:str) -> dict:
        """
        send video to streamdj and return a result

        Args:
            video_url: str - youtube video url 
            looks like `https://www.youtube.com/watch?v=POb02mjj2zE`

        Return:
            a dict object. can be:
                {'success': 1} - if success
                {'error': 'reason why'} - if error
        """
        if self._channel_id is None:
            self._update_channel_id()

        data = {
            "url": video_url,
            "author": self._author_name,
        }
        responce = requests.post(self._base_post_url % self._channel_id, data=data)
        responce = json.loads(responce.text)
        return responce

class YtPlaylist():
    """
    class to work with youtube playlist

    Args:
        api_key: str - google api key
        https://developers.google.com/youtube/registering_an_application

        list_id_or_url: str - youtube playlist id or url with playlist id
        for example https://www.youtube.com/playlist?list=AAA_AAAAAA-AAAAAAA is url
        AAA_AAAAAA-AAAAAAA is playlist id

    Examples:
        >>> y = YtPlaylist('KEYKEYKEY', 'LISTID')
        >>> y.videos
        [Video(title='Some video 1', url='https://www.youtube.com/watch?v=1111'),
         Video(title='Some video 2', url='https://www.youtube.com/watch?v=2222')]
    """
    def __init__(self, api_key:str, list_id_or_url:str):
        self._api_key = api_key
        if 'list=' in list_id_or_url:
            self._list_id = re.search(r'list=([a-zA-Z0-9-_]+)', list_id_or_url).group(1)
        else:
            self._list_id = list_id_or_url

        self._base_video_url = 'https://www.youtube.com/watch?v=%s'
        

    @property
    def videos(self):
        '''
        get all videos from playlist

        Return:
            namedtuple('Video', ('title', 'url'))
        '''
        videos = []
        nextPageToken = ''

        while 1:
            response = requests.get(f'https://www.googleapis.com/youtube/v3/playlistItems?\
                part=snippet&\
                maxResults={50}&\
                pageToken={nextPageToken}&\
                playlistId={self._list_id}&\
                key={self._api_key}\
                '.replace(' ', ''),
                timeout=10
            )
            
            jsn = json.loads(response.text)
            videos += self._fetch_videos_from_responce(jsn)
            
            if 'nextPageToken' not in jsn:
                break
            else:
                nextPageToken = jsn['nextPageToken']

        return videos

    def _fetch_videos_from_responce(self, jsn:dict):
        videos = []
        items = jsn['items']
        for item in items:
            video_id = item['snippet']['resourceId']['videoId']
            url = self._base_video_url % video_id
            title = item['snippet']['title']
            video = Video(title, url)
            videos.append(video)
        return videos

class Config():
    """
    class to work with config file
    """
    file_path = Path().home() / Path('.config') / Path('stream_dj') / Path('config')

    @staticmethod
    def get_api_key() -> str:
        file_path = Config.file_path
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'{file_path} not found')

        with open(file_path, 'r') as file:
            key = file.read()

        return key

    @staticmethod
    def set_api_key(key:str):
        file_path = Config.file_path
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path))

        with open(file_path, 'w') as file:
            file.write(key)

class Ui():
    """
    class with user interface
    """
    def __init__(self):
        self._hello_message = '''\
Wellcome to easy stream dj.
'''
        self._ex_channel_name = ''
        self._ex_cooldown = 0.0
        self._api_key = None

        self._threads = []
        self._is_sending_ended = False

    def _update_api_key(self):
        self._api_key = input('Google api key: ')
        Config.set_api_key(self._api_key)

    def _send_request_and_print_result(self, dj:StreamDj, video:Video):
        result = dj.send(video.url)
        if 'error' in result.keys():
            error = result["error"]
            result_str = f'{video.title}: {error}'
        else:
            result_str = f'{video.title}: Success.'
        print(result_str)

    def _check_if_sending_ended(self):
        for thread in self._threads:
            if thread.is_alive():
                return False
        return True

    def _loop(self):
        print()
        channel_name = input(f'channel name (default={self._ex_channel_name}): ')
        playlist = input(f'playlist: ')
        cooldown = input(f'cooldown (default={self._ex_cooldown}): ')

        if channel_name == '':
            channel_name = self._ex_channel_name
        if cooldown == '':
            cooldown = self._ex_cooldown
        if type(cooldown) is not float:
            cooldown = float(cooldown)

        self._ex_channel_name = channel_name
        self._ex_cooldown = cooldown

        videos = YtPlaylist(self._api_key, playlist).videos
        dj = StreamDj(channel_name)
        self._is_sending_ended = False
        for video in videos:
            thread = threading.Thread(target=self._send_request_and_print_result, args=(dj, video))
            self._threads.append(thread)
            thread.start()
            sleep(cooldown)

        
        while not self._check_if_sending_ended():
            sleep(1)

    def _help(self):
        print('''\
Wellcome to easy stream dj.

dj.py

[any args]      print this message

if you start this script for a first time:
    you need to enter yout Google Api Key

after script runing:
    channel name: nickname of streamdj user
    for example https://streamdj.ru/c/e6000000000 is url e6000000000 is channel name

    playlist: youtube playlist id or url with playlist id
    for example https://www.youtube.com/playlist?list=AAA_AAAAAA-AAAAAAA is url
    AAA_AAAAAA-AAAAAAA is playlist id

    cooldown: sleep time before next send


    if you leave some of this blank it will be replaced by default that shows you
            
''')

    def run(self):
        if sys.argv.__len__() >= 2:
            self._help()
            return

        if self._api_key is None:
            try:
                self._api_key = Config.get_api_key()
            except FileNotFoundError:
                self._update_api_key()

        print(self._hello_message)

        while 1:
            self._loop()

if __name__ == '__main__':
    try:
        Ui().run()
    except KeyboardInterrupt:
        print()
        exit(0)