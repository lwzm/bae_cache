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
    now.month, now.day, now.hour, now.minute, now.second, now.microsecond,
]))

try:
    import bae_image
    import bae_log.handlers
except ImportError:
    R = redis.StrictRedis()  # at localhost
else:
    M = pymongo.MongoClient("mongo.duapp.com", 8908)[etc.mongo]
    M.authenticate(etc.api_key, etc.secret_key)
    R = redis.StrictRedis("redis.duapp.com", 80, password="-".join([
        etc.api_key, etc.secret_key, etc.redis,
    ]))
    logging.getLogger().addHandler(
        bae_log.handlers.BaeLogHandler(etc.api_key, etc.secret_key)
    )
    def img():
        return bae_image.BaeImage(etc.api_key, etc.secret_key, "image.duapp.com")


if __name__ == "__main__":
    print(ID)
