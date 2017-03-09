#!/usr/bin/env python
from __future__ import unicode_literals
import youtube_dl
import json
import sys
import os
import logging

LOGNAME = "yt-playlists.log"

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler(LOGNAME)
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

LOCK = "yt-playlists.lock"
CONFIG = "yt-playlists.json"
config = None
dl_success = None

SAMPLE_CONFIG = """
{
    "options": {
        "format": "best"
    },
    "playlist": {
        "gu": {
            "last": 55,
            "match": "EP0?%d",
            "url": "https://www.youtube.com/playlist?list=PLpOa-OrneXm1-d7KBR7qff7ETu3qnRp_6"
        }, 
        "san": {
            "last": 16,
            "match": "EP0?%d",
            "url": "https://www.youtube.com/playlist?list=PLpOa-OrneXm34lESV2HJzCIFHA3tBrI5s"
        }
    }
}
"""


def lock():
    with open(LOCK, 'w') as f:
        # f is unused
        logging.info("yt-playlists locked")


def clean_exit():
    if os.path.isfile(LOCK):
        os.remove(LOCK)
        logging.info("yt-playlists unlocked")
        sys.exit()


def load_config():
    global config
    try:
        with open(CONFIG, 'r') as f:
            config = json.load(f)
    except:
        logging.error("Unable to load config file (%s). Exiting...", CONFIG)
        logging.debug("Sample config file:\n%s", SAMPLE_CONFIG)
        clean_exit()


def save_config():
    try:
        os.rename(CONFIG, CONFIG+".bak")  # in case next line fails and we end up with an empty file
        with open(CONFIG, 'w') as f:
            f.write(json.dumps(config, indent=4, sort_keys=True))
        os.remove(CONFIG+".bak")
    except:
        logging.error("Unable to write to config file (%s):\n", CONFIG)
        logging.debug(config)
        os.rename(CONFIG+".bak", CONFIG)
        logging.debug("%s has been restored.", CONFIG)
        clean_exit()


def download_eps(name=None, url=None, ep=None, match=None):
    """ Search and download given episode, and later ones if any.
    Return last downloaded episode number, ep-1 if ep is not found.
    
    name:   str, video name prefix
    url:    str, YouTube playlist URL
    ep:     int, start episode number
    match:  str, regex pattern to match
    """

    global dl_success
    dl_success = False

    def finish_hook(d):
        global dl_success
        if d["status"] == "finished":
            dl_success = True

    options = config["options"].copy()  # don't want to save the runtime options below in config
    options["matchtitle"] = match % ep
    options["outtmpl"] = "%s_%d.mp4" % (name, ep)
    options["progress_hooks"] = [finish_hook]

    with youtube_dl.YoutubeDL(options) as ytdl:
        logging.info("Started downloading %s", options["outtmpl"])
        ytdl.download([url])
    if dl_success:  # ytdl successfully downloaded specified video
        logging.info("Finished downloading %s", options["outtmpl"])
        return download_eps(name=name, url=url, ep=ep+1, match=match)  # try next episode
    else:
        logging.info("Unable to download %s", options["outtmpl"])
        return ep-1  # which is last downloaded episode number


if __name__=='__main__':
    if len(sys.argv) == 2:
        # pass any argument for sample json config
        print CONFIG
        print SAMPLE_CONFIG
        sys.exit()

    if os.path.isfile(LOCK):
        logging.error("Another process is running in this directory. Exiting...")
        sys.exit()
    else:
        lock()

    load_config()

    playlists = config["playlist"]
    for pl in playlists:
        last = playlists[pl]['last']
        latest = download_eps(name=pl, url=playlists[pl]['url'], ep=last+1, match=playlists[pl]['match'])
        if latest > last:
            logging.info("%s is now up to EP%d", pl, latest)
            playlists[pl]['last'] = latest
            save_config()
        else:
            logging.info("%s has no new video", pl)

    clean_exit()