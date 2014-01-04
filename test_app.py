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
app.debug = True


@app.route('/')
def app_index():
    return 'Hello, World!'

if __name__ == '__main__':
    from werkzeug_unix_sock import patch_werkzeug
    patch_werkzeug()
    app.run('test_app.dev.sock')
