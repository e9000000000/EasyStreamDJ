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

def GetVideosFromPlaylist(listID):
    videos = []
    nextPageToken = ''

    while 1:
        try:
            print(f'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet'
                + f'&maxResults={50}'
                + f'&pageToken={nextPageToken}'
                + f'&playlistId={listID}'
                + f'&key={API_KEY}')
            response = requests.get(f'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet\
                &maxResults={50}\
                &pageToken={nextPageToken}\
                &playlistId={listID}\
                &key={API_KEY}', timeout=7)
        except TimeoutError:
            return []
        
        jsn = json.loads(response.text)
        print(jsn)
        videos += get_videos_from_json(jsn)
        
        if 'nextPageToken' not in jsn:
            break

    return videos


def main():
    playlistID = input('youtube playlist id: ')
    chanel_name = input('streamDJ chanel_name: ')
    videos = GetVideosFromPlaylist(playlistID)
    threads = []

    for video in videos:
        thread = threading.Thread(target=print, args=(f'{video.title}: {send_music(chanel_name, video.GetUrl())}',))
        thread.start()

        threads.append(thread)

        

    


if __name__ == '__main__':
    main()
