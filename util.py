#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from __future__ import print_function, unicode_literals

import json
import os
import os.path

def persist(path, data):
    dir, _ = os.path.split(path)
    if dir and not os.path.isdir(dir):
        os.makedirs(dir)
    with open(path, "wb") as f:
        f.write(data)


def to_json(obj):
    return json.dumps(obj, indent=4, separators=(',', ': '),
                      default=str, sort_keys=True)
