#!/usr/bin/env python2
# -*- coding:utf-8 -*-
# http://developer.baidu.com/wiki/index.php?title=docs/cplat/rt/python

from __future__ import division, print_function, unicode_literals

import os.path

import requests
import tornado.log
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.wsgi

import util
        
        
class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Access-Control-Allow-Origin", "*")

    def options(self, obj):
        self.set_header("Access-Control-Allow-Headers",
                        "accept, content-type")
        self.set_header("Access-Control-Allow-Methods",
                        "GET, POST, PUT, DELETE, PATCH, OPTIONS")
        self.set_header("Access-Control-Max-Age", "3600")


class UploadHandler(BaseHandler):
    def post(self, path):
        """
        curl --data-binary @dump.rdb 'http://host/sync/backup/redis_db.bak'
        """
        util.persist(path, self.request.body)
    
    put = post
    
    def delete(self, path):
        util.remove_all(path)


class CacheHandler(BaseHandler):
    def get(self, path):
        data = util.get_path_data(path)
        self.set_header("Content-Type", "application/octet-stream")
        self.finish(data)


app = tornado.web.Application([
    (r"/upload/(.+)", UploadHandler),
    (r"/(.+)", CacheHandler),
])

wsgi_app = tornado.wsgi.WSGIAdapter(app)


if __name__ == "__main__":
    tornado.options.define("port", 1024, type=int)
    tornado.options.parse_command_line()
    app.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()
else:  # BAE
    import bae
    application = bae.create_wsgi_app(wsgi_app)