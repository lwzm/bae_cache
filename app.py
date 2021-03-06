#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from __future__ import division, print_function, unicode_literals

import mimetypes
import os
import os.path
import urllib

import requests
import tornado.log
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.wsgi

from tornado.escape import utf8, to_unicode

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
        if path.endswith("/"):
            os.makedirs(utf8(path))
        else:
            util.persist(path, self.request.body)

    put = post

    def delete(self, path):
        util.remove_all(path)


class CacheHandler(BaseHandler):
    #@tornado.web.removeslash
    def get(self, path):
        data = util.get_path_data(path)
        if data is None:
            raise tornado.web.HTTPError(404)
        mime_type, encoding = mimetypes.guess_type(path)
        self.set_header("Content-Type", mime_type or "application/octet-stream")
        self.finish(data)


class LogHandler(BaseHandler):
    def get(self, name):
        if name:
            n = int(self.get_argument("n", 30))
            self.set_header("Content-Type", "text/plain")
            self.write(b'\n'.join(util.view_log(name, n)))
        else:
            self.set_header("Content-Type", "text/html")
            logs = os.listdir("../log")
            self.write("""
            <!DOCTYPE html>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            """)
            for i in logs:
                self.write("<p><a href=/log/{} target=_blank>{}</a></p>".format(i[:-4], i))


app = tornado.web.Application([
    (r"/upload/(.+)", UploadHandler),
    (r"/log/(.*)", LogHandler),
    (r"/(.+)", CacheHandler),
])

from wsgi import WSGIApplication
application = WSGIApplication(tornado.wsgi.WSGIAdapter(app))


if __name__ == "__main__":
    tornado.options.define("port", 1024, type=int)
    tornado.options.parse_command_line()
    app.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()
