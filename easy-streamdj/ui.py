import argparse
import asyncio

from .youtube import Playlist, Video
from .streamdj import StreamDj
from .exceptions import StreamDjException


class Ui:
    """
    Class with user interface
    """

    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Easy way to use stream dj")

        self.parser.add_argument(
            "user", type=str, help="stream dj user name you want send music to"
        )
        self.parser.add_argument(
            "-v", "--video", type=str, metavar="URL", help="send youtube video"
        )
        self.parser.add_argument(
            "-p",
            "--playlist",
            type=str,
            metavar="URL",
            help="youtube playlist, all vidios from it will be send to stream dj",
        )
        self.parser.add_argument(
            "-P",
            "--playlistsearch",
            type=str,
            metavar="TEXT",
            help="same as --playlist, but it'll search for a playlist in youtube",
        )
        self.parser.add_argument(
            "-d",
            "--delay",
            type=float,
            metavar="SECONDS",
            help="delay between sending videos from playlist (float) defalut=0",
            default=0.0,
        )
        self.parser.add_argument(
            "-q",
            "--quantity",
            action="store_true",
            help="show quantity of tracks in stream dj.",
        )
        self.parser.add_argument(
            "-l", "--list", action="store_true", help="show all tracks in stream dj"
        )
        self.parser.add_argument(
            "-s",
            "--skip",
            action="store_true",
            help="(testing) send requests for skiping now playing track in stream dj",
        )
        self.parser.add_argument(
            "-a",
            "--author",
            type=str,
            metavar="NAME",
            help="author name of track sender",
        )
        self.args = self.parser.parse_known_args()[0]
        self.dj = StreamDj(self.args.user, self.args.author)

        self._threads = []
        self._is_sending_ended = False

    async def run(self):
        await self.dj.update_channel_id()
        if self.args.quantity or self.args.list or self.args.skip:
            tracks = await self.dj.track_list()
            if self.args.quantity:
                quantity = len(tracks)
                print(f"\n\ntracks quantity: {quantity}\n\n")
            if self.args.list:
                for track in tracks:
                    print(f"{track.author}: {track.title}\n{track.id=} {track.skip=}\n")
            if self.args.skip and tracks:
                await self.dj.update_proxy_list()
                track_id = tracks[0].id
                tasks = []
                for _ in range(await self.dj.get_proxy_amount()):
                    tasks.append(asyncio.create_task(self._vote_skip_and_print_result(track_id)))
                for task in tasks:
                    await task
        if self.args.video:
            await self._send_request_and_print_result(Video("Video", self.args.video))
        if self.args.playlist or self.args.playlistsearch:
            if self.args.playlistsearch:
                self.args.playlist = await self._chouse_playlist()
            tracks = await Playlist(self.args.playlist).get_videos()
            print(f"\n\nVideos fetched: {len(tracks)}\n\n")
            tasks = []
            for track in tracks:
                tasks.append(asyncio.create_task(self._send_request_and_print_result(track)))
                await asyncio.sleep(self.args.delay)

            for task in tasks:
                await task

    async def _chouse_playlist(self) -> Playlist:
        text = self.args.playlistsearch
        lists = await Playlist.search(text)
        print()
        for i, lst in enumerate(lists):
            print(f"[{i}] - videos({lst.videos_amount}): {lst.name}")
        try:
            i = int(input("chouse (blank or trash=0): "))
        except:
            i = 0
        return lists[i].url

    async def _send_request_and_print_result(self, video: Video):
        try:
            await self.dj.send(video.url)
            print(f"success sended: {video.title}")
        except StreamDjException as e:
            print(f"error while sending: {video.title=} {e=}")

    async def _vote_skip_and_print_result(self, track_id: int):
        try:
            await self.dj.vote_skip(track_id)
            print(f"success skip request: {track_id}")
        except StreamDjException as e:
            print(f"error while skiping: {track_id=} {e=}")
