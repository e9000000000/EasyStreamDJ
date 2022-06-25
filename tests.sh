#/bin/bash

echo "test channel> "
read CHANNEL
echo "test author name> "
read AUTHOR

echo "test video> "
read VIDEO
poetry run python . -v "$VIDEO" -a "$AUTHOR"

echo "test playlist> "
read PLAYLIST
poetry run python . -p "$PLAYLIST" -d 3

echo "test playlist search> "
read PLAYLIST_SEARCH
poetry run python . -P "$PLAYLIST_SEARCH" -d 3

poetry run python . -lq
