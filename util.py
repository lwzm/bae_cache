#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from __future__ import print_function, unicode_literals

import atexit
import datetime
import json
import gzip
import io
import os
import os.path
import shutil
import sys
import urllib
import traceback

import arrow
import redis
import tailer
import requests
import tornado.log
import tornado.options

from pony import orm
from pony.orm import Database, PrimaryKey, Required, Optional
from tornado.escape import utf8, to_unicode


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
    data = Required(buffer, lazy=True)
    time = Optional(datetime.datetime)
# mysql END


def bae_init():
    import bae
    orm.sql_debug(0)
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
        if "." in path[1:10]:  # looks like a domain
            resp = http_session.get("http://" + path)
            resp.raise_for_status()
            data = resp.content
            persist(path, data)
    else:
        persist_to_local(path, data)
    return data


def get_path_data_from_mysql(path):
    path = to_unicode(path)
    data = None
    with orm.db_session:
        try:
            data = bytes(File[path].data)
        except orm.core.ObjectNotFound:
            pass
    if not data:  # None or empty
        return data
    with io.BytesIO(data) as f:
        with gzip.GzipFile(mode="rb", fileobj=f) as g:
            try:
                data = g.read()
            except IOError:
                pass
    return data


def get_path_data_from_redis(path):
    path = utf8(path)
    n = redis_cli.llen(path)
    if not n:
        return
    delta = 250
    chunks = []
    for i in range(0, n, delta):
        chunks.extend(redis_cli.lrange(path, i, i + delta - 1))
    return b''.join(chunks)


def persist(path, data):
    persist_to_local(path, data)
    persist_to_mysql(path, data)


def persist_to_local(path, data):
    path = utf8(path)
    dir, _ = os.path.split(path)
    if dir and not os.path.isdir(dir):
        os.makedirs(dir)
    with open(path, "wb") as f:
        f.write(data)


def persist_to_mysql(path, data):
    path = to_unicode(path)
    with io.BytesIO() as f:
        with gzip.GzipFile(mode="wb", compresslevel=1, fileobj=f) as g:
            g.write(data)
        data = f.getvalue()
    with orm.db_session:
        try:
            f = File[path]
            f.data = data
        except orm.core.ObjectNotFound:
            f = File(path=path, data=data)
        f.time = datetime.datetime.now()


def persist_to_redis(path, data):
    path = utf8(path)
    step = 2048 - 256
    redis_cli.delete(path)
    for i in range(0, len(data), step):
        redis_cli.rpush(path, data[i:i+step])


def remove_all(path):
    path = utf8(path)
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


def iter_filenames_in_directory(path):
    path = utf8(path)
    for dirpath, dirnames, filenames in os.walk(path):
        for fn in filenames:
            yield os.path.join(dirpath, fn)


# only once
try:
    bae_init()
except ImportError:
    pass


if __name__ == "__main__":
    pass
