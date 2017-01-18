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
wsgi_app = tornado.wsgi.WSGIAdapter(app)


if __name__ == "__main__":
    tornado.options.define("port", 1024, type=int)
    tornado.options.parse_command_line()
    app.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()
    #import wsgiref.simple_server
    #wsgiref.simple_server.make_server("0.0.0.0", 1024, wsgi_app).serve_forever()

else:  # BAE
    util.bae_init(os.path.basename(__file__))
    import bae
    application = bae.create_wsgi_app(wsgi_app)
