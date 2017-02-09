#!/usr/bin/env python
from __future__ import unicode_literals
import youtube_dl
import json
import sys

CONFIG = "yt-playlists.json"
config = None
dl_status = None

""" ### sample config ###

{
    "options": {
        "format": "best"
    },
    "playlist": {
        "gu": {
            "last": 55,
            "url": "https://www.youtube.com/playlist?list=PLpOa-OrneXm1-d7KBR7qff7ETu3qnRp_6"
        }, 
        "san": {
            "last": 16,
            "url": "https://www.youtube.com/playlist?list=PLpOa-OrneXm34lESV2HJzCIFHA3tBrI5s"
        }
    }
}

"""


def load_config():
    global config
    try:
        with open(CONFIG, 'r') as f:
            config = json.load(f)
    except:
        print ">> Unable to load config file (%s). Exiting..." % CONFIG
        sys.exit()


def save_config():
    global config
    try:
        with open(CONFIG, 'w') as f:
            f.write(json.dumps(config, indent=4, sort_keys=True))
    except:
        print ">> Unable to write to config file (%s):\n"
        #print json.dumps(config, indent=4, sort_keys=True)
        print config
        sys.exit()


def download_eps(name=None, url=None, ep=None):
    """ Search and download given episode, and later ones if any.
    Return last downloaded episode number, ep-1 if ep is not found.
    
    url:    str, YouTube playlist URL
    ep:     int, start episode number
    """

    global dl_status
    dl_status = False

    def finish_hook(d):
        global dl_status
        if d["status"] == "finished":
            dl_status = True

    title_regex = "EP" + ("0" + str(ep) if ep < 10 else str(ep))
    options = config["options"].copy()  # don't want to save changes below in config
    options["matchtitle"] = title_regex
    options["outtmpl"] = name+"_"+title_regex+".mp4"
    options["progress_hooks"] = [finish_hook]

    with youtube_dl.YoutubeDL(options) as ytdl:
        ytdl.download([url])
    if dl_status:  # ytdl successfully downloaded specified video
        return download_eps(name=name, url=url, ep=ep+1)  # try next episode
    else:
        return ep-1  # which is last downloaded episode number


if __name__=='__main__':
    load_config()

    for pl in config["playlist"]:
        last = config['playlist'][pl]['last']
        latest = download_eps(name=pl, url=config['playlist'][pl]['url'], ep=last+1)
        if latest > last:
            print ">> %s is now up to EP%d" % (pl, latest)
            config['playlist'][pl]['last'] = latest
            save_config()
        else:
            print ">> %s has no new video" % pl
