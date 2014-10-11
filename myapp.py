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
import json
import time

import sh
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


def cache_it(path):
    try:
        data = tornado.httpclient.HTTPClient().fetch("http://" + path).body
    except Exception:
        data = b''  # do not care status code
    persist(path, data)
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
            self.render("dir.html", ls=[i + "/" * os.path.isdir(os.path.join(path, i))
                                        for i in os.listdir(path)])
        else:
            environ = tornado.wsgi.WSGIContainer.environ(self.request)
            self.set_header("Content-type", "text/plain")
            self.write(json.dumps(environ, indent=4, separators=(',', ': '),
                                  default=str, sort_keys=True))


class ShellHandler(BaseHandler):
    shell = Shell()
    shell.push("import " + ",".join(set(map(
        lambda s: s.split(".")[0], filter(
            lambda s: not s.startswith("_"), sys.modules)))))
    shell.push("""def q(s): c, _, a = s.partition(" "); return getattr(sh, c)(*a.split())""")
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
        persist(path, self.request.body)


class CacheHandler(BaseHandler):
    def get(self, host, path):
        self.set_header("Content-Type", "application/octet-stream")
        self.finish(cache_it("{0}/{1}".format(host, path)))  # should use finish, not write, why?


app = tornado.web.Application([
    (r"/shell", ShellHandler),
    (r"/sync/(.+)", SyncHandler),
    (r"/([^.]+\..*[^.])/(.+[^/])", CacheHandler),
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
    tornado.log.enable_pretty_logging()
    import bae
    application = bae.create_wsgi_app(wsgi_app, debug)
