#!/usr/bin/env python2
# -*- coding:utf-8 -*-
# http://developer.baidu.com/wiki/index.php?title=docs/cplat/rt/python

from __future__ import print_function, unicode_literals

import code
import collections
import io
import os
import os.path
import sys
import time

import tornado.httpclient
import tornado.log
import tornado.options
import tornado.web
import tornado.wsgi

import res

debug = True


def persist(path, data):
    dir, _ = os.path.split(path)
    if dir and not os.path.isdir(dir):
        os.makedirs(dir)
    with open(path, "wb") as f:
        f.write(data)


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
        r = res.R
        environ = tornado.wsgi.WSGIContainer.environ(self.request)
        r.sadd("keys", res.ID)
        r.hset(res.ID, time.time(), environ.get("HTTP_USER_AGENT"))
        self.set_header("Content-type", "text/plain")
        self.write("\n".join([
            self.request.remote_ip,
            res.ID,
            str(r.smembers("keys")),
        ]))


class ShellHandler(BaseHandler):
    shell = Shell()
    shell.push("import sh, res, sys, os")

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
        "TODO"

    def post(self, path):
        """
        curl --data-binary @dump.rdb 'http://host/sync/backup/redis_db.bak'
        """
        persist(path, self.request.body)


class CacheTemporaryHandler(BaseHandler):
    def get(self, path):
        prefix = "http://tmp.qww.pw/"
        response = tornado.httpclient.HTTPClient().fetch(prefix + path)
        persist("tmp/" + path, response.body)  # do not care status code
        self.finish(response.body)  # should use finish, not write, why?


app = tornado.web.Application([
    (r"/shell", ShellHandler),
    (r"/sync/(.*)", SyncHandler),
    (r"/tmp/(.*)", CacheTemporaryHandler),
    (r"/(.*)", MainHandler),
], static_path="static", template_path="template", debug=debug)

wsgi_app = tornado.wsgi.WSGIAdapter(app)

tornado.options.options.log_file_prefix = b"../log/myapp.log"  # should be str in py2, :(
tornado.log.enable_pretty_logging()


if __name__ == "__main__":
    port = 1024
    app.listen(port)
    tornado.ioloop.IOLoop.instance().start()
    import wsgiref.simple_server
    #wsgiref.simple_server.make_server("0.0.0.0", port, wsgi_app).serve_forever()
else:
    import bae
    application = bae.create_wsgi_app(wsgi_app, debug)
