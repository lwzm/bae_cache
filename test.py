#!/usr/bin/env python2
# -*- coding:utf-8 -*-

def app(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/plain')]
    start_response(status, headers)
    body = [str(environ)]
    return body


import bae
application = bae.create_wsgi_app(app, True)
