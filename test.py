#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import util


def app(environ, start_response):
    status = "200 OK"
    headers = [("Content-type",  "application/octet-stream")]
    if environ["REQUEST_METHOD"] == "GET":
        body = util.to_json(environ)
    else:
        body = environ["wsgi.input"].read(int(environ["CONTENT_LENGTH"]))
    start_response(status, headers)
    return body


import bae
application = bae.create_wsgi_app(app, True)
