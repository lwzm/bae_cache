#!/usr/bin/env python3

import datetime
import json
import os
import os.path
import sys
import urllib

import requests


def interactive_upload(dir=None):
    def g_input():
        while True:
            try:
                path = input()
                yield path
            except EOFError:
                break

    def g_walk_dir():
        for dirpath, dirnames, filenames in os.walk(dir):
            for fn in filenames:
                yield os.path.join(dirpath, fn)

    if dir is None:
        it = g_input()
    else:
        it = g_walk_dir()

    ss = requests.Session()

    for path in it:
        with open(path, "rb") as f:
            data = f.read()
        resp = ss.put(
            "http://pycache.duapp.com/upload/" + path, data=data)
        print(resp.status_code, path, len(data))


if __name__ == "__main__":
    interactive_upload(*sys.argv[1:])
