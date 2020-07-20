import requests
import json
import os
from random import randrange

def generateRandomAuthorName():
    h = hash(randrange(0, 2281377))
    if (type(h) is str):
        return h
    return str(h)

def GetLinksList():
    """from links.json file"""
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "links.json")) as file:
        jText = file.read()
    return json.loads(jText)

def GetChanelIdByStreamDjLink(link):
    responce = requests.get(link).text
    findSignature = "onclick=\"add_track("
    startIndex = responce.index(findSignature) + len(findSignature)
    endIndex = responce.index(")", startIndex)
    return responce[startIndex:endIndex]

def SendMusic(chanelID, youtubeURL) -> bool:
    data = {
        "url": youtubeURL,
        "author": generateRandomAuthorName(),
    }

    responce = requests.post("https://streamdj.ru/includes/back.php?func=add_track&channel=" + chanelID, data=data)
    responce = json.loads(responce.text)
    return [x for x in responce.values()][0]

def RandomConsistentNumberList(lenght):
    lst = [x for x in range(lenght)]
    for x in range(lenght):
        index1 = randrange(0, lenght)
        index2 = randrange(0, lenght)
        lst[index1], lst[index2] = lst[index2], lst[index1]

    return lst