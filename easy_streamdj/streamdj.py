import asyncio
import errno
import re
import random
from collections import namedtuple
from time import sleep

import aiohttp
import names

from .exceptions import StreamDjException


Track = namedtuple("Video", ("id", "title", "author", "skip"))


class StreamDj:
    """
    class to work with streamdj.app

    Args:
        channel_name: str - nickname of streamdj user
        for example https://streamdj.app/c/e6000000000 is url e6000000000 is channel name

        author_name: str - name that will shows as a sender of music
        if leave it `None` it will generates by names lib. generated names looks like `Victor Owens` `Regina Franks`

    Examples:
        >>> s = StreamDj('someone')
        >>> s.send('https://www.youtube.com/watch?v=POb02mjj2zE')
        {'success': 1}
    """

    _channel_url_template = "https://streamdj.app/c/{name}"
    _track_list_url_template = "https://streamdj.app/includes/back.php?func=playlist&channel={channel_id}&c="
    _send_url_template = (
        "https://streamdj.app/includes/back.php?func=add_track&channel={channel_id}"
    )
    _vote_skip_url = "http://streamdj.app/includes/back.php?func=vote_skip"
    _proxy_list_url = (
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
    )

    def __init__(self, channel_name: str, author_name: str | None = None):
        self._channel_name = channel_name
        self._custom_author_name = author_name

        self._channel_id: str | None = None
        self._proxies: list[str] | None = None


    async def track_list(self) -> list[Track]:
        """get list of tracks from streamdj"""

        if self._channel_id is None:
            raise ValueError("update channel id before")

        url = self._track_list_url_template.format(channel_id=self._channel_id)

        async with aiohttp.request("GET", url) as response:
            if response.status // 100 != 2:
                raise ConnectionError(
                    f"cant get tracks from {self._channel_name}, status_code={response.status}"
                )

            jsn = await response.json(content_type=None)

        tracks = []
        if not jsn:
            return []

        for i in jsn:
            track = jsn[i]
            tracks.append(
                Track(track["id"], track["title"], track["author"], track["skip"])
            )
        return tracks

    async def send(self, track_url: str):
        """
        send track to streamdj and return a result

        Args:
            track_url: str - youtube video url
            looks like `https://www.youtube.com/watch?v=POb02mjj2zE`

        raise `StreamDjException` if track is not sended
        """

        if self._channel_id is None:
            raise ValueError("update channel id before")

        response = await self._request(
            self._send_url_template,
            {"channel_id": self._channel_id},
            {
                "url": track_url,
                "author": self._author_name,
            },
        )
        error = response.get("error", None)
        if error is not None:
            raise StreamDjException(error)

    async def vote_skip(self, track_id: int):
        if self._proxies is None:
            raise ValueError("update proxy list before")
        if self._channel_id is None:
            raise ValueError("update channel id before")

        if not await self.get_proxy_amount():
            raise StreamDjException("no proxies")

        proxy = random.choice(self._proxies)
        self._proxies.remove(proxy)
        proxy = f"http://{proxy}"
        data = {
            "channel": str(self._channel_id),
            "track_id": str(track_id),
        }
        while True:
            try:
                response = await self._request(self._vote_skip_url, {}, data, proxy)
                error = response.get("error", None)
                if error is not None:
                    raise StreamDjException(error)
            except OSError as e:
                if e.errno != errno.ETOOMANYREFS:
                    raise e
                await asyncio.sleep(10)

    @property
    def _author_name(self):
        if self._custom_author_name is not None:
            return self._custom_author_name
        return names.get_full_name()

    async def _request(
        self, url_template: str, url_params: dict, data: dict, proxy: str | None = None
    ) -> dict:
        url = url_template.format(**url_params)

        async with aiohttp.request("POST", url, data=data, proxy=proxy, timeout=aiohttp.ClientTimeout(total=60)) as response:

            if response.status >= 500:
                sleep(5)
                return await self._request(url_template, url_params, data, proxy)

            if response.status // 100 != 2:
                raise ConnectionError(
                    f"error while sending request {url=} to {self._channel_name=}, {response.status=}."
                )

            try:
                return await response.json(content_type=None)
            except Exception as e:  # if response not in json format
                print(e)
                text = await response.text(encoding="utf-8")
                if "Technical problems, come back later." in text:
                    sleep(5)
                    return await self._request(url_template, url_params, data, proxy)
                else:
                    return {
                        "error": f"Does not sended cuz streamdj.app is great. response: {text}"
                    }

    async def get_proxy_amount(self):
        if self._proxies is None:
            raise ValueError("update proxy list before")
        return len(self._proxies)


    async def update_proxy_list(self):
        """get proxy list from github repository"""

        url = self._proxy_list_url
        async with aiohttp.request("GET", url) as response:


            if response.status // 100 != 2:
                raise ConnectionError(f"cant get proxy list {response.status=}")

            text = await response.text()

        self._proxies = text.splitlines()

    async def update_channel_id(self):
        """get channel id from streamdj"""

        url = self._channel_url_template.format(name=self._channel_name)
        async with aiohttp.request("GET", url) as response:

            if response.status == 404:
                raise ValueError(f"channel with {self._channel_name=} does not exist.")
            elif response.status // 100 != 2:
                raise ConnectionError(f"can't update channel id {response.status=}")

            text = await response.text()

        result = re.search(r"onclick=\"add_track\(([0-9]+)\)\"", text)
        if result is None:
            raise ValueError(f"cant find channel id. {self._channel_name=}")

        self._channel_id = result.group(1)
