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
import cgi

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
                    background-color: #1a1a1a;
                    color: #e0e0e0;
                    margin: 0;
                    padding: 20px;
                }
                h2 {
                    background-color: #8b0000;
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                    font-size: 0.9em;
                }
                ul {
                    list-style-type: none;
                    padding: 0;
                }
                li {
                    margin: 5px 0;
                    padding: 8px;
                    background-color: #2b2b2b;
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
                .upload-form {
                    margin-top: 20px;
                    padding: 10px;
                    background-color: #333;
                    border: 1px solid #444;
                    border-radius: 5px;
                    display: flex;
                    align-items: center;
                    justify-content: flex-start;
                }
                .upload-form input[type="file"] {
                    margin-right: 10px;
                    color: #e0e0e0;
                    background-color: #2b2b2b;
                    border: 1px solid #444;
                    border-radius: 5px;
                    padding: 5px;
                    width: auto;
                    cursor: pointer;
                }
                .upload-form input[type="file"]::-webkit-file-upload-button {
                    background-color: #8b0000;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px;
                    font-size: 0.9em;
                    cursor: pointer;
                    transition: background-color 0.3s;
                }
                .upload-form input[type="file"]::-webkit-file-upload-button:hover {
                    background-color: #a83232;
                }
                .upload-form input[type="submit"] {
                    background-color: #8b0000;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-size: 0.9em;
                    cursor: pointer;
                    transition: background-color 0.3s;
                }
                .upload-form input[type="submit"]:hover {
                    background-color: #a83232;
                }
                #success-modal {
                    display: none;
                    position: fixed;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    background-color: #4CAF50;
                    color: white;
                    padding: 20px;
                    border-radius: 5px;
                    z-index: 1000;
                }
                #success-modal.fade-in {
                    display: block;
                    animation: fadeIn 0.5s;
                }
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
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
        r.append('</ul>')
        r.append('''
            <hr>
            <form enctype="multipart/form-data" method="post" class="upload-form">
                <input name="file" type="file" />
                <input type="submit" value="Upload"/>
            </form>
            <div id="success-modal">File uploaded successfully</div>
            <script>
                function showSuccessModal() {
                    const modal = document.getElementById('success-modal');
                    modal.classList.add('fade-in');
                    setTimeout(() => { modal.classList.remove('fade-in'); }, 3000);
                }

                if (window.location.search.includes("uploaded=true")) {
                    showSuccessModal();
                    window.history.replaceState({}, document.title, window.location.pathname);
                }

                document.querySelector('input[type="file"]').classList.add('styled-file-input');
            </script>
        ''')
        r.append('</body></html>')
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
        content_type, pdict = cgi.parse_header(self.headers['Content-Type'])
        if content_type == 'multipart/form-data':
            pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
            pdict['CONTENT-LENGTH'] = int(self.headers['Content-Length'])
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'}, keep_blank_values=True)
            if 'file' in form:
                file_item = form['file']
                filename = os.path.basename(file_item.filename)
                upload_path = os.path.join(self.translate_path(self.path), filename)
                with open(upload_path, 'wb') as output_file:
                    output_file.write(file_item.file.read())
                self.send_response(303)
                self.send_header('Location', self.path + '?uploaded=true')
                self.end_headers()
                logging.info("POST request,\nPath: %s\nHeaders:\n%s\nFile: %s\n",
                             str(self.path), str(self.headers), filename)
            else:
                self.send_error(400, "File field missing in the form submission")
        else:
            self.send_error(400, "Invalid form submission")
            return

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

def run(server_class=ThreadingSimpleServer, handler_class=FancyHTTPRequestHandler, port=80):
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
