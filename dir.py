#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from __future__ import division, print_function, unicode_literals

import io
import os
import os.path
import urllib
import zipfile
import tarfile

import humanize
import tornado.log
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.wsgi

from tornado.escape import utf8, to_unicode

import util


class BaseHandler(tornado.web.RequestHandler):
    pass


class DirectoryHandler(BaseHandler):
    def get(self, path="."):
        download = self.get_argument("dl", None)
        if download:
            cwd = os.getcwd()
            try:
                os.chdir(utf8(path))
                self._download_dir_package(path, download)
            finally:
                os.chdir(cwd)
            return

        dirs, files = [], []
        path = utf8(path)
        for i in os.listdir(path):
            p = os.path.join(path, i)
            try:
                st = os.stat(p)
            except OSError:
                continue
            padding = " " * (30 - len(i))
            if os.path.isdir(p):
                dirs.append(
                    (i + "/", padding + "{:>15}".format(st.st_nlink))
                )
            else:
                files.append(
                    (i, padding + "{:>16}".format(humanize.naturalsize(st.st_size, gnu=True)))
                )
        lst = sorted(dirs) + sorted(files)
        self.render("dir.html", path=path, lst=lst)

    def _download_dir_package(self, path, type):
        filename = os.path.basename(path) + "." + type
        self.set_header("Content-Type", "application/octet-stream")
        self.set_header("Content-Disposition", "attachment; filename=" + filename)
        f = io.BytesIO()
        if type == "zip":
            with zipfile.ZipFile(f, "w", zipfile.ZIP_DEFLATED) as zip:
                for fn in util.iter_filenames_in_directory("."):
                    zip.write(fn)
        elif type == "tar":
            with tarfile.open(None, "w", f) as tar:
                for fn in os.listdir("."):
                    tar.add(fn)
        value = f.getvalue()
        f.close()
        self.finish(value)

    def post(self, path=""):
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

from wsgi import WSGIApplication
application = WSGIApplication(tornado.wsgi.WSGIAdapter(app))


if __name__ == "__main__":
    tornado.options.define("port", 1024, type=int)
    tornado.options.parse_command_line()
    app.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()
