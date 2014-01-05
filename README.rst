Werkzeug + Unix sockets
=======================

Monkey-patching Werkzeug WSGI server to use Unix sockets instead of TCP
sockets.

Why?
----

Because I was tired of having to deal with looking for free TCP ports for my
Flask development servers. Using Unix sockets is much simpler and fun.

How?
----

Here's a quick guide to using Werkzeug + Unix sockets in a Flask app.

First, install the module:

.. sourcecode:: console

    $ pip install git+git://github.com/tomekwojcik/werkzeug_plus_unix_sockets.git

Then, adapt your app to use it:

.. sourcecode:: python

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

Finally, you'll have to adapt your nginx config:

.. sourcecode:: nginx

    server {
        server_name unix_sock_demo.app;
        listen      127.0.0.1:80;

        location / {
            proxy_pass  http://unix:/tmp/unix_sock_demo.app.sock:;
            proxy_set_header Host $host;
        }
    }

Restart nginx, start your app and test it:

.. sourcecode:: console

    bilbo ~ $ http -v GET http://unix_sock_demo.app/
    GET / HTTP/1.1
    Accept: */*
    Accept-Encoding: gzip, deflate, compress
    Host: unix_sock_demo.app
    User-Agent: HTTPie/0.7.2



    HTTP/1.1 200 OK
    Connection: keep-alive
    Content-Length: 13
    Content-Type: text/html; charset=utf-8
    Date: Sun, 05 Jan 2014 12:49:30 GMT
    Server: nginx/1.4.2

    Hello, World!

Will it work with my Flask app?
-------------------------------

It works with mine Flask apps, so it should work with yours, too. I can't
guarantee anything, though. I tested it with a few Flask apps of
mine, each one using ``Werkzeug==0.9.4``.

Since this is an ugly hack all I can say that your mileage may vary.

Anything else?
--------------

This hack was done by `Tomek Wójcik <http://www.bthlabs.pl/>`_. Since it
borrows code from Werkzeug, it's licensed under the BSD license.
