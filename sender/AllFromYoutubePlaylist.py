API_KEY = ''


import requests
import json
import threading

from sender.Sender import GetChanelIdByStreamDjLink, SendMusic


class YtVideo():
    def __init__(self, ID, title):
        self.id = ID
        self.title = title

    def GetUrl(self):
        return f'https://www.youtube.com/watch?v={self.id}'

def GetYtVideosFromJson(js):
    videos = []
    items = js['items']
    for item in items:
        video = YtVideo(item['snippet']['resourceId']['videoId'], item['snippet']['title'])
        videos.append(video)
    return videos

def GetVideosFromPlaylist(listID):
    videos = []
    nextPageToken = ''

    while 1:
        r = requests.get(f'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults={50}&pageToken={nextPageToken}&playlistId={listID}&key={API_KEY}')
        js = json.loads(r.text)
        videos += GetYtVideosFromJson(js)
        
        try:
            nextPageToken = js['nextPageToken']
        except:
            break

    return videos


def main():
    playlistID = input('youtube playlist id: ')
    chanelId = GetChanelIdByStreamDjLink(input('streamDJ link: '))
    videos = GetVideosFromPlaylist(playlistID)

    for video in videos:
        def send():
            print(f'{video.title}: {SendMusic(chanelId, video.GetUrl())}')
        threading.Thread(target=send).start()

        

    


if __name__ == '__main__':
    main()
