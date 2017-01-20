#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from __future__ import division, print_function, unicode_literals

import os
import os.path
import urllib

import tornado.log
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.wsgi

import util
        
        
class BaseHandler(tornado.web.RequestHandler):
    pass


class DirectoryHandler(BaseHandler):
    def get(self, path="."):
        path = urllib.unquote(path.encode("utf-8"))
        dirs, files = [], []
        for i in os.listdir(path):
            if os.path.isdir(os.path.join(path, i)):
                dirs.append(i + '/')
            else:
                files.append(i)
        lst = sorted(dirs) + sorted(files)
        self.render("dir.html", path=path, lst=lst)
        
    def post(self, path="."):
        if "file" not in self.request.files:
            return
        file_obj = self.request.files["file"][0]
        path = os.path.join(path, file_obj["filename"])
        data = file_obj["body"]
        util.persist(path, data)
        
        
app = tornado.web.Application([
        (r"/", DirectoryHandler),
        (r"/(.+)/", DirectoryHandler),
    ],
    static_path="static",
    template_path="templates",
)

wsgi_app = tornado.wsgi.WSGIAdapter(app)


if __name__ == "__main__":
    tornado.options.define("port", 1024, type=int)
    tornado.options.parse_command_line()
    app.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()
else:  # BAE
    import bae
    application = bae.create_wsgi_app(wsgi_app)
