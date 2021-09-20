import requests
import names
from time import sleep
import re


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
        self._channel_url_template = "https://streamdj.ru/c/%s"
        self._send_url_template = (
            "https://streamdj.ru/includes/back.php?func=add_track&channel=%s"
        )

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

        data = {
            "url": video_url,
            "author": self._author_name,
        }
        response = requests.post(
            self._send_url_template % self._channel_id, data=data, timeout=120
        )

        if response.status_code >= 500:
            sleep(5)
            return self.send(video_url)

        if response.status_code != 200:
            raise ConnectionError(
                f"try to send {video_url} to {self._channel_name}, status_code={response.status_code}."
            )

        try:
            return response.json()
        except Exception:  # if response not in json format
            if "Technical problems, come back later." in response.text:
                sleep(5)
                return self.send(video_url)
            else:
                return {
                    "error": f"Does not sended cuz streamdj.ru is great. response: {response.text}"
                }

    @property
    def _author_name(self):
        if self._custom_author_name is not None:
            return self._custom_author_name
        return names.get_full_name()

    def _update_channel_id(self):
        response = requests.get(self._channel_url_template % self._channel_name)

        if response.status_code == 404:
            raise ValueError(f"channel with name={self._channel_name} does not exist.")
        elif response.status_code != 200:
            raise ConnectionError(f"status_code={response.status_code}")

        result = re.search(r"onclick=\"add_track\(([0-9]+)\)\"", response.text)

        if result is None:
            raise ValueError(f"cant find channel id. channel_name={self._channel_name}")

        self._channel_id = result.group(1)
