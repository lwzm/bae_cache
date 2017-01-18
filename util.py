#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from __future__ import print_function, unicode_literals

import atexit
import json
import os.path
import shutil

import arrow
import tornado.log
import tornado.options


def bae_init(basename):
    fn = "../log/start_stop.log"
    start = arrow.now()

    with open(fn, "a") as f:
        print("start", os.getpid(), basename, start, sep="\t", file=f)

    def exit():
        stop = arrow.now()
        with open(fn, "a") as f:
            print("stop", os.getpid(), basename, stop, stop - start, sep="\t", file=f)

    atexit.register(exit)

    #tornado.options.options.log_file_prefix = b'../log/_{}.log'.format(basename)  # should be str in py2, and .. is /home/bae/
    tornado.options.options.log_file_prefix = b'../log/my_app.log'
    try:
        tornado.log.enable_pretty_logging()
    except Exception:
        traceback.print_exc()
        
        
def persist(path, data):
    dir, _ = os.path.split(path)
    if not dir:
        raise ValueError(path)
    if not os.path.isdir(dir):
        os.makedirs(dir)
    with open(path, "wb") as f:
        f.write(data)
        

def remove_all(path):
    if os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)

        
def to_json(obj):
    return json.dumps(obj, indent=4, separators=(',', ': '),
                      default=str, sort_keys=True)
