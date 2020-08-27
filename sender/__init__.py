import requests
import json
import os
import names
from random import randrange

def __generate_random_author_name():
    return names.get_full_name()

def __get_chanelId(chanel_name):
    responce = requests.get(f'https://streamdj.ru/c/{chanel_name}').text
    findSignature = "onclick=\"add_track("
    startIndex = responce.index(findSignature) + len(findSignature)
    endIndex = responce.index(")", startIndex)
    return responce[startIndex:endIndex]

def send_music(chanel_name, youtube_url) -> str:
    data = {
        "url": youtube_url,
        "author": __generate_random_author_name(),
    }

    responce = requests.post("https://streamdj.ru/includes/back.php?func=add_track&channel=" + __get_chanelId(chanel_name), data=data)
    responce = json.loads(responce.text)
    return responce.__str__()