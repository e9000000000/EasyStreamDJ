from dj.ui import Ui


if __name__ == '__main__':
    try:
        Ui().run()
    except KeyboardInterrupt:
        print()
        exit(0)