import sender.EndlessSenderByLink as EndlessSenderByLink
import sender.EnterToSendFromJson as EnterToSendFromJson
import sender.SendAllFronJson as SendAllFronJson
import sender.AllFromYoutubePlaylist as AllFromYoutubePlaylist

def main():
    print("streamDJ easy sender")
    print("")
    print("type number to start:")
    print("    1) sending by typing url")
    print("    2) sending step by step by url from links.json")
    print("    3) sending all by url from links.json")
    print("    4) sending all by url from links.json")
    print("")

    while 1:
        try:
            inp = int(input())
            if inp == 1:
                EndlessSenderByLink.main()
            elif inp == 2:
                EnterToSendFromJson.main()
            elif inp == 3:
                SendAllFronJson.main()
            elif inp == 4:
                AllFromYoutubePlaylist.main()
            else:
                print("enter a number from 1 to 3")
                continue

        except:
            print("is this a number?")
            pass

if __name__ == "__main__":
    main()