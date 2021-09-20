import sys
from threading import Thread
from time import sleep

from .youtube import Playlist, Video
from .streamdj import StreamDj


class Ui:
    """
    Class with user interface
    """

    _hello_message = "Wellcome to easy stream dj."
    _help_message = """
    Wellcome to easy stream dj.

    dj.py

    [any args]      print this message

    After script runing:
        channel name: nickname of streamdj user
        for example https://streamdj.ru/c/e6000000000 is url e6000000000 is channel name

        playlist: youtube playlist id or url with playlist id
        for example https://www.youtube.com/playlist?list=AAA_AAAAAA-AAAAAAA is url
        AAA_AAAAAA-AAAAAAA is playlist id

        cooldown: sleep time before next send


        If you leave some of this blank it will be replaced by default that shows you.

    """

    def __init__(self):
        self._ex_channel_name = ""
        self._ex_cooldown = 0.0
        self._api_key = None

        self._threads = []
        self._is_sending_ended = False

    def run(self):
        if sys.argv.__len__() >= 2:
            print(self._help_message)
            return

        print(self._hello_message)

        while 1:
            self._loop()

    def _send_request_and_print_result(self, dj: StreamDj, video: Video):
        result = dj.send(video.url)
        if "error" in result.keys():
            error = result["error"]
            result_str = f"{video.title}: {error}"
        else:
            result_str = f"{video.title}: Success."
        print(result_str)

    def _check_if_sending_ended(self):
        for thread in self._threads:
            if thread.is_alive():
                return False
        return True

    def _loop(self):
        print()
        channel_name = input(f"channel name (default={self._ex_channel_name}): ")
        playlist = input("playlist: ")
        cooldown = input(f"cooldown (default={self._ex_cooldown}): ")

        if channel_name == "":
            channel_name = self._ex_channel_name
        if cooldown == "":
            cooldown = self._ex_cooldown
        if type(cooldown) is not float:
            cooldown = float(cooldown)

        self._ex_channel_name = channel_name
        self._ex_cooldown = cooldown

        videos = Playlist(playlist).get_videos()
        print(f"\n\nVideos fetched: {len(videos)}\n\n")
        dj = StreamDj(channel_name)
        self._is_sending_ended = False
        for video in videos:
            thread = Thread(
                target=self._send_request_and_print_result, args=(dj, video)
            )
            self._threads.append(thread)
            thread.start()
            sleep(cooldown)

        while not self._check_if_sending_ended():
            sleep(1)
