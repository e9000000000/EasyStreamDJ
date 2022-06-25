import asyncio

from .ui import Ui


if __name__ == "__main__":
    try:
        asyncio.run(Ui().run())
    except KeyboardInterrupt:
        print()
        exit(0)
