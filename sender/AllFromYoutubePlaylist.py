import requests
import json
import threading

from config import API_KEY
from . import send_music


class YtVideo():
    def __init__(self, ID, title):
        self.id = ID
        self.title = title

    def GetUrl(self):
        return f'https://www.youtube.com/watch?v={self.id}'

def get_videos_from_json(jsn):
    videos = []
    items = jsn['items']
    for item in items:
        video = YtVideo(item['snippet']['resourceId']['videoId'], item['snippet']['title'])
        videos.append(video)
    return videos

def get_videos_from_playlist(listID):
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
        videos += get_videos_from_json(jsn)
        
        if 'nextPageToken' not in jsn:
            break
        else:
            nextPageToken = jsn['nextPageToken']

    return videos


def send_and_print_result(chanel_name, video):
    result = send_music(chanel_name, video.GetUrl())
    readable_result = f'{list(result.keys())[0]} {list(result.values())[0]}'

    print(f'{video.title}: {readable_result}')

def main():
    playlistID = input('youtube playlist id: ')
    chanel_name = input('streamDJ chanel_name: ')
    videos = get_videos_from_playlist(playlistID)

    for video in videos:
        thread = threading.Thread(target=send_and_print_result, args=(chanel_name, video))
        thread.start()
        

    


if __name__ == '__main__':
    main()
