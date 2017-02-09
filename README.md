# YouTube Drama Downloader

This script is to help me keep track and download new drama episodes from Youtube playlists, **in time**, for my wife :-)

`yt-playlists.json` contains download options, playlists and most importantly, the last downloaded episode number. So that previously downloaded & watched & deleted episodes are not re-downloaded.

`yt-playlist-dl.py` is expected to run by cron job to check and download new episodes in the plylists if any. Luckily the dramas have `EPxx` in the title to help identify them. So I can use the built-in `matchtitle` option of `youtube-dl` to select an episode from playlist to download.

## Dependency ##

Install Python package:

    sudo pip install --upgrade youtube_dl

Full installation details see [https://rg3.github.io/youtube-dl/download.html](https://rg3.github.io/youtube-dl/download.html).

## Cron Jobs ##

You should add two cron jobs: (1) to run the downloader at set intervals; (2) to upgrade your `youtube-dl` package frequently to pick up new updates that match YouTube's changes on their website.

Here's mine:

    # update youtube-dl package daily at 6am
    0 6 * * * sudo pip install --upgrade youtube_dl

    # run the downloader daily at given hours
    0 2 * * * cd /path/to/dramas/ ; /path/to/yt-playlist-dl.py

