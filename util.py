#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from __future__ import print_function, unicode_literals

import atexit
import datetime
import json
import os
import os.path
import shutil
import sys
import urllib

import arrow
import pony
import redis
import tailer
import requests
import tornado.log
import tornado.options

from pony import orm
from pony.orm import Database, PrimaryKey, Required, Optional


AK = "6618acb85fd85fe7ee98e086ecad7744"
SK = "9561d86f7cb1e5b9a5a03fc0e24011c9"
REDIS_NAME = "JzKrsXlZwABgPxwlLPIp"
MYSQL_NAME = "OLIiOHWoBlwdNKjKXCta"

range = xrange

http_session = ss = requests.Session()

redis_cli = rd = redis.StrictRedis(
    "redis.duapp.com", 80, password="-".join([AK, SK, REDIS_NAME]))


# mysql
db = Database()

class File(db.Entity):
    path = PrimaryKey(unicode)
    data = Required(buffer)
    time = Optional(datetime.datetime)
# mysql END


def bae_init():
    fn = "../log/start_stop.log"
    start = arrow.now()

    with open(fn, "a") as f:
        print("start", os.getpid(), start, sep="\t", file=f)

    def exit():
        stop = arrow.now()
        with open(fn, "a") as f:
            print("stop", os.getpid(), stop, stop - start, sep="\t", file=f)

    atexit.register(exit)

    #tornado.options.options.log_file_prefix = b'../log/_{}.log'.format(basename)  # should be str in py2, and .. is /home/bae/
    tornado.options.options.log_file_prefix = b'../log/my_app.log'
    try:
        tornado.log.enable_pretty_logging()
    except Exception:
        traceback.print_exc()

    db.bind("mysql", host="sqld.duapp.com", port=4050, user=AK, passwd=SK, db=MYSQL_NAME)
    db.generate_mapping(create_tables=True)
        
        
def get_path_data(path):
    data = get_path_data_from_mysql(path)
    if data is None:
        resp = http_session.get("http://" + path)
        resp.raise_for_status()
        data = resp.content
        persist(path, data)
    else:
        persist_to_local(path, data)
    return data


def get_path_data_from_mysql(path):
    if not isinstance(path, unicode):
        path = path.decode("utf-8")
    data = None
    with orm.db_session:
        try:
            data = bytes(File[path].data)
        except orm.core.ObjectNotFound:
            pass
    return data

    
def get_path_data_from_redis(path):
    n = redis_cli.llen(path)
    if not n:
        return
    delta = 250
    chunks = []
    for i in range(0, n, delta):
        chunks.extend(redis_cli.lrange(path, i, i + delta - 1))
    return b''.join(chunks)

    
def persist(path, data):
    path = urllib.unquote(path)
    persist_to_local(path, data)
    persist_to_mysql(path, data)

        
def persist_to_local(path, data):
    if isinstance(path, unicode):
        path = path.encode("utf-8")
    dir, _ = os.path.split(path)
    if dir and not os.path.isdir(dir):
        os.makedirs(dir)
    with open(path, "wb") as f:
        f.write(data)


def persist_to_mysql(path, data):
    if not isinstance(path, unicode):
        path = path.decode("utf-8")
    with orm.db_session:
        try:
            f = File[path]
            f.data = data
        except orm.core.ObjectNotFound:
            f = File(path=path, data=data)
        f.time = datetime.datetime.now()
        

def persist_to_redis(path, data):
    step = 2048 - 256
    redis_cli.delete(path)
    for i in range(0, len(data), step):
        redis_cli.rpush(path, data[i:i+step])

        
        
def remove_all(path):
    if os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)

        
def to_json(obj):
    return json.dumps(obj, indent=4, separators=(',', ': '),
                      default=str, sort_keys=True)


def view_log(name, n=50):
    with open("../log/{}.log".format(name)) as f:
        lines = tailer.tail(f, n)
    return lines

    
# only once
try:
    import bae
    bae_init()
except ImportError:
    pass


def interactive_upload(dir=None):
    def g_input():
        input = raw_input
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
            b'http://pycache.duapp.com/upload/' + path, data=data)
        print(resp.status_code, path, len(data))



if __name__ == "__main__":
    interactive_upload(*sys.argv[1:])
