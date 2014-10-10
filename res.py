#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from __future__ import print_function, unicode_literals

import datetime
import logging

import pymongo
import redis

import etc

now = datetime.datetime.now()

ID = "-".join(map(str, [
    now.hour, now.minute, now.second, now.microsecond,
]))

try:
    import bae
except ImportError:
    R = redis.StrictRedis()  # at localhost
else:
    M = pymongo.Connection(host="mongo.duapp.com", port=8908)[etc.mongo]
    M.authenticate(etc.api_key, etc.secret_key)
    R = redis.StrictRedis("redis.duapp.com", 80, password="-".join([
        etc.api_key, etc.secret_key, etc.redis,
    ]))




try:
    import bae_log.handlers
except ImportError:
    pass
else:
    logging.getLogger().addHandler(
        bae_log.handlers.BaeLogHandler(etc.api_key, etc.secret_key)
    )


if __name__ == "__main__":
    print(ID)
