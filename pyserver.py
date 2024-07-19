#!/usr/bin/env python3

"""
License: MIT License
Copyright (c) 2023 Miel Donkers

Very simple HTTP server in python for logging requests
Usage::
    ./pyserver.py [<port>]

This project was inspired by the work of Miel Donkers
See: https://gist.github.com/mdonkers/63e115cc0c79b4f6b8b3a6b797e485c7
"""

from http.server import SimpleHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import os
import logging
from colorlog import ColoredFormatter

class FancyHTTPRequestHandler(SimpleHTTPRequestHandler):
    def _set_response(self, code=200, content_type='text/html'):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def list_directory(self, path):
        """Generate a directory listing."""
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        displaypath = os.path.relpath(path, self.directory)
        title = 'Directory listing for %s' % displaypath
        r = []
        r.append('<!DOCTYPE html>')
        r.append('<html><head><title>%s</title>' % title)
        r.append('''
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #1e1e1e;
                    color: #e0e0e0;
                    margin: 0;
                    padding: 20px;
                }
                h2 {
                    background-color: #b71c1c;
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                    font-size: 1.2em;
                }
                ul {
                    list-style-type: none;
                    padding: 0;
                }
                li {
                    margin: 5px 0;
                    padding: 8px;
                    background-color: #2a2a2a;
                    border: 1px solid #444;
                    border-radius: 5px;
                    transition: background-color 0.3s;
                }
                li a {
                    text-decoration: none;
                    color: #f44336;
                    font-weight: bold;
                }
                li:hover {
                    background-color: #3a3a3a;
                }
                hr {
                    border: none;
                    height: 1px;
                    background-color: #444;
                    margin: 20px 0;
                }
            </style>
        ''')
        r.append('</head>')
        r.append('<body><h2>%s</h2>' % title)
        r.append('<ul>')
        r.append('<li><a href="..">..</a></li>')  # Link to the parent directory
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            r.append('<li><a href="%s">%s</a></li>' % (linkname, displayname))
        r.append('</ul><hr></body></html>')
        encoded = '\n'.join(r).encode('utf-8', 'surrogateescape')
        self.wfile.write(encoded)

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        if os.path.isdir(self.translate_path(self.path)):
            self._set_response()
            self.list_directory(self.translate_path(self.path))
        else:
            super().do_GET()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                     str(self.path), str(self.headers), post_data.decode('utf-8'))
        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

def setup_logging():
    """Setup logging with color."""
    formatter = ColoredFormatter(
        "%(log_color)s%(levelname)s:%(name)s:%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO, handlers=[handler])

def run(server_class=ThreadingSimpleServer, handler_class=FancyHTTPRequestHandler, port=8080):
    setup_logging()
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting pyserver...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping pyserver...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
