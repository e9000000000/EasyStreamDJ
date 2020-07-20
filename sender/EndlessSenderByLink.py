from sender.Sender import GetChanelIdByStreamDjLink, SendMusic


def main():
    chanelID = GetChanelIdByStreamDjLink(input("stream dj url: "))

    while 1:
        musicURL = input("youtube url: ")
        print(SendMusic(chanelID, musicURL))


if __name__ == "__main__":
    main()