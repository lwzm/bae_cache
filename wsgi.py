import sys
import urllib
import os


class WSGIApplication:
    def __init__(self, app, debug=False):
        self.app = app
        self.debug = debug

    def sanitize(self, environ):
        environ['SCRIPT_NAME'] = ''
        reqUri = None
        
        if environ.has_key('REQUEST_URI'):
            reqUri = environ['REQUEST_URI'].split('?', 1)
            
        if reqUri is not None:
            environ['PATH_INFO'] = urllib.unquote(reqUri[0])
        else:
            environ['PATH_INFO'] = ''

        if reqUri is not None and len(reqUri) > 1:
            environ['QUERY_STRING'] = reqUri[1]
        else:
            environ['QUERY_STRING'] = ''

    def __call__(self, environ, start_response):
        self.sanitize(environ)

        if not self.debug:
            return self.app(environ, start_response)

        try:
            return self.app(environ, start_response)
        except Exception, e:
            start_response("500 Internal Server Error", [('Content-type', 'text/plain')])
            import traceback
            info = traceback.format_exc()
            return [info]
