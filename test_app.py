# -*- coding: utf-8 -*-
"""
test_app
========

This module provides a Flask application that uses patched Werkzeug WSGI
server.
"""

import sys
sys.path.insert(0, '.')

from flask import Flask

app = Flask(__name__)


@app.route('/')
def app_index():
    return 'Hello, World!'

if __name__ == '__main__':
    app.debug = True

    try:
        from werkzeug_unix_sock import patch_werkzeug
    except ImportError:
        app.run() # Falling back to TCP socket.
    else:
        patch_werkzeug()
        app.run('/tmp/unix_sock_demo.app.sock') # Using Unix socket.
