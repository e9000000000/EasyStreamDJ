import requests
import json
import threading
from time import sleep

from config import API_KEY
from . import send_music


class YtVideo():
    def __init__(self, ID, title):
        self.id = ID
        self.title = title

    def GetUrl(self):
        return f'https://www.youtube.com/watch?v={self.id}'

def __get_videos_from_json(jsn):
    videos = []
    items = jsn['items']
    for item in items:
        video = YtVideo(item['snippet']['resourceId']['videoId'], item['snippet']['title'])
        videos.append(video)
    return videos

def __get_videos_from_playlist(listID):
    videos = []
    nextPageToken = ''

    while 1:
        try:
            response = requests.get(f'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet'
                + f'&maxResults={50}'
                + f'&pageToken={nextPageToken}'
                + f'&playlistId={listID}'
                + f'&key={API_KEY}', timeout=7)
        except TimeoutError:
            return []
        
        jsn = json.loads(response.text)
        videos += __get_videos_from_json(jsn)
        
        if 'nextPageToken' not in jsn:
            break
        else:
            nextPageToken = jsn['nextPageToken']

    return videos


def __send(result_list, channel_name, video):
    result = send_music(channel_name, video.GetUrl())
    readable_result = f'{list(result.keys())[0]} {list(result.values())[0]}'

    result_list.append(f'{video.title}: {readable_result}')

def __send_all(results, channel_name:str, videos, cooldown:int):
    for video in videos:
        threading.Thread(target=__send, args=(results, channel_name, video)).start()
        sleep(cooldown)

def process_results(results, max_lenght):
    already_yielded_count = 0
    while results.__len__() < max_lenght:
        for i in range(already_yielded_count, results.__len__()):
            yield results[i]
            already_yielded_count += 1
        sleep(0.05)


def send_from_playlist(channel_name:str, playlistID:str, cooldown:int):
    videos = __get_videos_from_playlist(playlistID)
    results = []

    threading.Thread(target=__send_all, args=(results, channel_name, videos, cooldown)).start()

    for result in process_results(results, videos.__len__()):
        yield result

