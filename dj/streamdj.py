import requests
import names
from time import sleep
import re
import random
from collections import namedtuple


Video = namedtuple("Video", ("id", "title", "author", "skip"))


class StreamDj:
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

    def __init__(self, channel_name: str, author_name: str = None):
        self._channel_name = channel_name
        self._custom_author_name = author_name

        self._channel_id = None
        self._proxy_list = None

        self._channel_url_template = "https://streamdj.ru/c/{name}"
        self._videos_list_url_template = "https://streamdj.ru/includes/back.php?func=playlist&channel={channel_id}&c="
        self._send_url_template = (
            "https://streamdj.ru/includes/back.php?func=add_track&channel={channel_id}"
        )
        self._vote_skip_url = "https://streamdj.ru/includes/back.php?func=vote_skip"
        self._proxy_list_url = (
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
        )

    def videos_list(self) -> list[Video]:
        """
        get list of videos from streamdj

        Return:
            list of namedtuple("Video", ("title", "author"))
        """

        if self._channel_id is None:
            self._update_channel_id()

        response = requests.get(
            self._videos_list_url_template.format(channel_id=self._channel_id)
        )

        if response.status_code != 200:
            raise ConnectionError(
                f"cant get videos from {self._channel_name}, status_code={response.status_code}"
            )

        videos = []
        jsn = response.json()
        if not jsn:
            return []

        for i in jsn:
            video = jsn[i]
            videos.append(
                Video(video["id"], video["title"], video["author"], video["skip"])
            )
        return videos

    def send(self, video_url: str) -> dict:
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
        return self._request(
            self._send_url_template,
            {"channel_id": self._channel_id},
            {
                "url": video_url,
                "author": self._author_name,
            },
        )

    def vote_skip(self, video_id: int) -> None:
        if self._proxy_list is None:
            self._update_proxy_list()
        if self._channel_id is None:
            self._update_channel_id()

        if not len(self._proxy_list):
            return {"error": "proxies ended"}

        proxy = random.choice(self._proxy_list)
        self._proxy_list.remove(proxy)
        return self._request(
            self._vote_skip_url,
            {},
            {
                "channel": str(self._channel_id),
                "track_id": str(video_id),
            },
            {"https": f"http://{proxy}"},
        )

    @property
    def _author_name(self):
        if self._custom_author_name is not None:
            return self._custom_author_name
        return names.get_full_name()

    def _request(
        self, url_template: str, url_params: dict, data: dict, proxies: dict = {}
    ) -> dict:
        url = url_template.format(*url_params)

        response = requests.post(url, data=data, timeout=120, proxies=proxies)

        if response.status_code >= 500:
            sleep(5)
            return self._request(url_template, url_params, data)

        if response.status_code != 200:
            raise ConnectionError(
                f"try to send {url} to {self._channel_name}, status_code={response.status_code}."
            )

        try:
            return response.json()
        except Exception:  # if response not in json format
            if "Technical problems, come back later." in response.text:
                sleep(5)
                return self._request(url_template, url_params, data)
            else:
                return {
                    "error": f"Does not sended cuz streamdj.ru is great. response: {response.text}"
                }

    def _update_proxy_list(self):
        response = requests.get(self._proxy_list_url)

        if response.status_code != 200:
            raise ConnectionError(f"cant get proxy list {response.status_code=}")

        self._proxy_list = response.text.split("\n")

    def _update_channel_id(self):
        response = requests.get(
            self._channel_url_template.format(name=self._channel_name)
        )

        if response.status_code == 404:
            raise ValueError(f"channel with name={self._channel_name} does not exist.")
        elif response.status_code != 200:
            raise ConnectionError(f"status_code={response.status_code}")

        result = re.search(r"onclick=\"add_track\(([0-9]+)\)\"", response.text)

        if result is None:
            raise ValueError(f"cant find channel id. channel_name={self._channel_name}")

        self._channel_id = result.group(1)
