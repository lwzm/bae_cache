#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from __future__ import print_function, unicode_literals

import datetime
import logging

import redis

import etc

now = datetime.datetime.now()

ID = "-".join(map(str, [
    now.hour, now.minute, now.second, now.microsecond,
]))

R = redis.StrictRedis("redis.duapp.com", 80, password="-".join([
    etc.api_key, etc.secret_key, etc.redis,
]))

try:
    import bae
except ImportError:
    R = redis.StrictRedis()  # at localhost


try:
    import pymongo
    mongo_conn = pymongo.Connection(host="mongo.duapp.com", port=8908)
    M = mongo_conn[etc.mongo]
    M.authenticate(etc.api_key, etc.secret_key)
except:
    pass

try:
    import bae_log.handlers
    logging.getLogger().addHandler(
        bae_log.handlers.BaeLogHandler(etc.api_key, etc.secret_key)
    )
except:
    pass


if __name__ == "__main__":
    print(ID)
