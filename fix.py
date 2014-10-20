#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import util

import sh

def app(environ, start_response):
    sh.chmod("775", "../log")
    start_response("200 OK", [])
    return ""


import bae
application = bae.create_wsgi_app(app, True)
