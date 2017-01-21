#-*- coding:utf-8 -*-

import json

def app(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/plain')]
    start_response(status, headers)
    body = json.dumps(
        environ, default=str, indent=4, separators=(",", ": "),
        ensure_ascii=False, sort_keys=True,
    )
    return [body]

from wsgi import WSGIApplication
application = WSGIApplication(app)
