import unittest

from dj import youtube
from dj import streamdj


TEST_CHANNEL_NAME = input("channel name for test: ")
TEST_PLAYLIST = input("test playlist url or id: ")
TEST_PLAYLIST_LENGTH = int(input("test playlist length: "))


class TestYoutubeModule(unittest.TestCase):
    def test_send_request(self):
        playlist = youtube.Playlist(TEST_PLAYLIST)
        length = len(playlist.get_videos())
        self.assertEqual(
            length,
            TEST_PLAYLIST_LENGTH,
            "sometheing wrong with fetching videos from playlist",
        )


class TestStreamDjModule(unittest.TestCase):
    def test_get_channel_id(self):
        dj = streamdj.StreamDj(TEST_CHANNEL_NAME)
        dj._update_channel_id()
        self.assertEqual(dj._channel_id.isnumeric(), True, "cant get channel id")

    def test_send(self):
        dj = streamdj.StreamDj(TEST_CHANNEL_NAME)
        dj.send("https://www.youtube.com/watch?v=Fcu5PZcqhQc")


if __name__ == "__main__":
    unittest.main()
