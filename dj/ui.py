import argparse
from threading import Thread
from time import sleep

from .youtube import Playlist, Video
from .streamdj import StreamDj


class Ui:
    """
    Class with user interface
    """

    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Easy way to use stream dj.")

        self.parser.add_argument(
            "user", type=str, help="stream dj user name you want send music to."
        )
        self.parser.add_argument(
            "-p",
            "--playlist",
            type=str,
            help="youtube playlist, all vidios from it will be send to stream dj.",
        )
        self.parser.add_argument(
            "-d",
            "--delay",
            type=float,
            help="delay between sending videos from playlist (float) defalut=0",
            default=0.0,
        )
        self.parser.add_argument(
            "-q",
            "--quantity",
            action="store_true",
            help="show quantity of videos in stream dj.",
        )
        self.parser.add_argument(
            "-l", "--list", action="store_true", help="show all videos in stream dj."
        )
        self.args = self.parser.parse_args()
        self.dj = StreamDj(self.args.user)

        self._threads = []
        self._is_sending_ended = False

    def run(self):
        if self.args.quantity:
            quantity = len(self.dj.videos_list())
            print(f"\n\nvideos quantity: {quantity}\n\n")
        if self.args.list:
            for video in self.dj.videos_list():
                print(f"{video.author}: {video.title}")
        if self.args.playlist:
            videos = Playlist(self.args.playlist).get_videos()
            print(f"\n\nVideos fetched: {len(videos)}\n\n")
            for video in videos:
                thread = Thread(
                    target=self._send_request_and_print_result, args=(video,)
                )
                self._threads.append(thread)
                thread.start()
                sleep(self.args.delay)

            while not self._check_if_sending_ended():
                sleep(1)

    def _send_request_and_print_result(self, video: Video):
        result = self.dj.send(video.url)
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
