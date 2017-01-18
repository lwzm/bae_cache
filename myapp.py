#!/usr/bin/env python2
# -*- coding:utf-8 -*-
# http://developer.baidu.com/wiki/index.php?title=docs/cplat/rt/python

from __future__ import division, print_function, unicode_literals

import base64
import code
import collections
import io
import logging
import os
import os.path
import shlex
import sys
import time
import traceback

import requests
import sh
import tornado.httpclient
import tornado.log
import tornado.options
import tornado.web
import tornado.wsgi

try:
    import res
except Exception:
    traceback.print_exc()

import util

debug = True


def cache_it(path):
    data = b''
    try:
        data = tornado.httpclient.HTTPClient().fetch("http://" + path).body
    except tornado.httpclient.HTTPError as e:
        if e.code >= 500:
            raise
    util.persist(path, data)
    return data


class Shell(code.InteractiveInterpreter):
    def __init__(self):
        # super().__init__()  # py3
        code.InteractiveInterpreter.__init__(self)
        self.buf = []

    def push(self, line):
        buf = self.buf
        buf.append(line.rstrip())
        source = "\n".join(buf)

        more = False
        stdout, stderr = sys.stdout, sys.stderr
        output = sys.stdout = sys.stderr = io.BytesIO()
        try:
            more = self.runsource(source)
        finally:
            sys.stdout, sys.stderr = stdout, stderr

        if more:
            return None

        del buf[:]
        return output.getvalue()


class BaseHandler(tornado.web.RequestHandler):
    pass


class MainHandler(BaseHandler):
    def get(self, path):
        if not path:
            path = "."
        if os.path.isdir(path):
            p = lambda i: os.path.join(path, i)
            self.render("dir.html", ls=[
                (i + "/" * os.path.isdir(p(i)), os.stat(p(i)).st_size)
                for i in os.listdir(path)
            ])
        else:
            environ = tornado.wsgi.WSGIContainer.environ(self.request)
            self.set_header("Content-type", "text/plain")
            self.write(util.to_json(environ))


class ShellHandler(BaseHandler):
    shell = Shell()
    shell.push("import " + ",".join(set(map(
        lambda s: s.split(".")[0], filter(
            lambda s: not s.startswith("_"), sys.modules)))))
    shell.push("""def q(s): c, _, a = s.partition(" "); return getattr(sh, c)(*map(sh.glob, shlex.split(a)))""")
    shell.push("")

    def get(self):
        self.render("shell.html")

    def post(self):
        # from urllib.parse import unquote  # py3
        from urlparse import unquote
        input = unquote(self.request.body.decode("utf-8"))
        output = self.shell.push(input)
        if output is not None:
            self.write("\n" + output)


class SyncHandler(BaseHandler):
    def get(self, path):
        self.write(path)

    def post(self, path):
        """
        curl --data-binary @dump.rdb 'http://host/sync/backup/redis_db.bak'
        """
        util.persist(path, self.request.body)


class CacheHandler(BaseHandler):
    def get(self, host, path):
        self.set_header("Content-Type", "application/octet-stream")
        self.finish(cache_it("{0}/{1}".format(host, path)))  # should use finish, not write, why?


class QRCodeHandler(BaseHandler):
    def get(self, text):
        # from urllib.parse import unquote  # py3
        from urlparse import unquote
        img = res.img()
        img.setQRCodeText(unquote(text.encode("utf-8")))  # fuck...
        img.setQRCodeLevel(int(self.get_argument("level", 1)))
        img.setQRCodeSize(int(self.get_argument("size", 10)))
        img.setQRCodeVersion(int(self.get_argument("version", 0)))
        img.setQRCodeForeground(self.get_argument("foreground", "000000"))
        img.setQRCodeBackground(self.get_argument("background", "FFFFFF"))
        self.set_header("Content-Type", "image/gif")
        self.finish(base64.b64decode(
            img.process()["response_params"]["image_data"]))



app = tornado.web.Application([
    (r"/qr/(.+)", QRCodeHandler),
    (r"/shell", ShellHandler),
    (r"/sync/(.+)", SyncHandler),
    (r"/([^.]+\..*[^.])/(.*[^/])", CacheHandler),
    (r"/(.*)", MainHandler),
], static_path="static", template_path="template", debug=debug)

wsgi_app = tornado.wsgi.WSGIAdapter(app)


if __name__ == "__main__":
    tornado.options.define("port", 1024, type=int)
    tornado.options.parse_command_line()
    app.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()
    #import wsgiref.simple_server
    #wsgiref.simple_server.make_server("0.0.0.0", 1024, wsgi_app).serve_forever()
else:
    tornado.options.options.log_file_prefix = b"../log/myapp.log"  # should be str in py2, :(
    try:
        tornado.log.enable_pretty_logging()
    except Exception:
        traceback.print_exc()
    import bae
    application = bae.create_wsgi_app(wsgi_app, debug)
