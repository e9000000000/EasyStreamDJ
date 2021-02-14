import unittest
import requests

from dj import youtube
from dj import streamdj


TEST_CHANNEL_NAME = input('channel name for test: ')
TEST_PLAYLIST = input('test playlist url or id: ')


class TestYoutubeModule(unittest.TestCase):
    def test_api_key(self):
        url_template = 'https://www.googleapis.com/youtube/v3/search?key={key}'
        response = requests.get(url_template.format(
            key=youtube.GOOGLE_API_KEY
        ))

        self.assertEqual(
            response.status_code, 200,
            'GOOGLE_API_KEY env variable is not correct'
        )

    def test_send_request(self):
        playlist = youtube.Playlist(TEST_PLAYLIST)
        response = playlist._send_request() 
        self.assertEqual(
            response.status_code, 200,
            'sometheing wrong with _send_request method'
        )

    def test_fetch_videos_from_json(self):
        playlist = youtube.Playlist(TEST_PLAYLIST)
        response = playlist._send_request()
        videos = playlist._fetch_videos_from_json(response.json())
        self.assertNotEqual(
            videos.__len__(), 0,
            'cant fetch videos from json'
        )

    def test_get_videos_by_url(self):
        playlist = youtube.Playlist(TEST_PLAYLIST)
        self.assertNotEqual(
            playlist.videos.__len__(), 0,
            'cant get videos'
        )


class TestStreamDjModule(unittest.TestCase):
    def test_get_channel_id(self):
        dj = streamdj.StreamDj(TEST_CHANNEL_NAME)
        dj._update_channel_id()
        self.assertEqual(
            dj._channel_id.isnumeric(), True,
            'cant get channel id'
        )

    def test_send(self):
        dj = streamdj.StreamDj(TEST_CHANNEL_NAME)
        dj.send('https://www.youtube.com/watch?v=Fcu5PZcqhQc')












if __name__ == '__main__':
    unittest.main()