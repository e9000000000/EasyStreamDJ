import sender.Sender as ts
import threading


def main():
    chanelID = ts.GetChanelIdByStreamDjLink(input("stream dj url: "))
    links = ts.GetLinksList()
    linksOrder = ts.RandomConsistentNumberList(len(links))

    for i in range(len(links)):
        input()
        def send():
            print(f"{i + 1}: {ts.SendMusic(chanelID, links[linksOrder[i]])}")
        threading.Thread(target=send).start()


if __name__ == "__main__":
    main()