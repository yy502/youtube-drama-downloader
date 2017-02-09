# YouTube Drama Downloader

This script is to help me keep track and download new drama episodes from Youtube playlists, **in time**, for my wife :-)

`yt-playlists.json` contains download options, playlists and most importantly, the last downloaded episode number. So that previously downloaded & watched & deleted episodes are not re-downloaded.

`yt-playlist-dl.py` is expected to run by cron job to check and download new episodes in the plylists if any. Luckily the dramas have `EPxx` in the title to help identify them. So I can use the built-in `matchtitle` option of `youtube-dl` to select an episode from playlist to download.