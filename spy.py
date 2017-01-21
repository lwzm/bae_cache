#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from __future__ import division, print_function, unicode_literals

import atexit
import os.path

import tornado.log
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.wsgi

import util
import tornadospy


app = tornadospy.make_app()

from wsgi import WSGIApplication
application = WSGIApplication(tornado.wsgi.WSGIAdapter(app))


if __name__ == "__main__":
    tornado.options.define("port", 1024, type=int)
    tornado.options.parse_command_line()
    app.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()