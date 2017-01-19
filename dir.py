#!/usr/bin/env python2
# -*- coding:utf-8 -*-
# http://developer.baidu.com/wiki/index.php?title=docs/cplat/rt/python

from __future__ import division, print_function, unicode_literals

import os

import tornado.log
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.wsgi

import util
        
        
class BaseHandler(tornado.web.RequestHandler):
    pass


class DirectoryHandler(BaseHandler):
    def get(self, path):
        dirs, files = [], []
        for i in os.listdir(path):
            if os.path.isdir(os.path.join(path, i)):
                dirs.append(i + "/")
            else:
                files.append(i)
        lst = sorted(dirs) + sorted(files)
        self.render("dir.html", path=path, lst=lst)

app = tornado.web.Application([
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
