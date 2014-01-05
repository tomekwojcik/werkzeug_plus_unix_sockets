# -*- coding: utf-8 -*-
"""
werkzeug_unix_socket
====================

Monkey-patching Werkzeug WSGI server to use Unix sockets instead of TCP
sockets.
"""

import new
import os
import socket

import werkzeug.serving

__all__ = ['patch_werkzeug']
__version__ = '0.1'

CLIENT_ADDRESS = ('<local>', 0)


class WerkzeugPatcher(object):
    """This class provides interface to the patcher."""

    def __init__(self):
        self._orig_werkzeug_serving_WSGIRequestHandler_init = None
        self._orig_werkzeug_serving_select_ip_version = None
        self._orig_werkzeug_serving_BaseWSGIServer_init = None
        self._orig_werkzeug_serving_BaseWSGIServer_get_request = None
        self._orig_werkzeug_serving_run_simple = None

    def _patch_werkzeug_serving_WSGIRequestHandler_init(self):
        """Patches ``werkzeug.serving.WSGIRequestHandler.__init__`` method."""
        def new_init(inst, *args, **kwargs):
            super(inst.__class__, inst).__init__(*args, **kwargs)
            inst.client_address = CLIENT_ADDRESS

        self._orig_werkzeug_serving_WSGIRequestHandler_init =\
            werkzeug.serving.WSGIRequestHandler.__init__

        werkzeug.serving.WSGIRequestHandler.__init__ = new.instancemethod(
            new_init, None, werkzeug.serving.WSGIRequestHandler
        )

    def _patch_werkzeug_serving_select_ip_version(self):
        """Patches ``werkzeug.serving.select_ip_version`` function."""
        self._orig_werkzeug_serving_select_ip_version =\
            werkzeug.serving.select_ip_version

        werkzeug.serving.select_ip_version = lambda host, port: socket.AF_UNIX

    def _patch_werkzeug_serving_BaseWSGIServer_init(self):
        """Patches ``werkzeug.serving.BaseWSGIServer.__init__`` method."""
        def new_init(inst, host, port, app, handler=None,
                     passthrough_errors=False, ssl_context=None):
            if handler is None:
                handler = werkzeug.serving.WSGIRequestHandler

            inst.address_family = werkzeug.serving.select_ip_version(host,
                                                                     port)

            if os.path.exists(host):
                os.unlink(host)

            werkzeug.serving.HTTPServer.__init__(inst, host, handler)
            inst.app = app
            inst.passthrough_errors = passthrough_errors
            inst.shutdown_signal = False
            inst.ssl_context = None

            if ssl_context is not None:
                raise RuntimeError('SSL is not supported with UNIX sockets')

        self._orig_werkzeug_serving_BaseWSGIServer_init =\
            werkzeug.serving.BaseWSGIServer.__init__

        werkzeug.serving.BaseWSGIServer.__init__ = new.instancemethod(
            new_init, None, werkzeug.serving.BaseWSGIServer
        )

    def _patch_werkzeug_serving_BaseWSGIServer_get_request(self):
        """Patches ``werkzeug.serving.BaseWSGIServer.get_request`` method."""
        def new_get_request(inst):
            con, _ = super(inst.__class__, inst).get_request()
            return con, CLIENT_ADDRESS

        self._orig_werkzeug_serving_BaseWSGIServer_get_request =\
            werkzeug.serving.BaseWSGIServer.get_request

        werkzeug.serving.BaseWSGIServer.get_request = new.instancemethod(
            new_get_request, None, werkzeug.serving.BaseWSGIServer
        )

    def _patch_werkzeug_serving_run_simple(self):
        """Patches ``werkzeug.serving.run_simple`` function."""
        def new_run_simple(hostname, port, application, use_reloader=False,
                           use_debugger=False, use_evalex=True,
                           extra_files=None, reloader_interval=1,
                           threaded=False, processes=1,
                           request_handler=None, static_files=None,
                           passthrough_errors=False, ssl_context=None):
            if use_debugger:
                from werkzeug.debug import DebuggedApplication
                application = DebuggedApplication(application, use_evalex)
            if static_files:
                from werkzeug.wsgi import SharedDataMiddleware
                application = SharedDataMiddleware(application, static_files)

            def inner():
                server = werkzeug.serving.make_server(
                    hostname, port, application, threaded,
                    processes, request_handler,
                    passthrough_errors, ssl_context
                )
                server.serve_forever()

            if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
                quit_msg = '(Press CTRL+C to quit)'
                werkzeug.serving._log(
                    'info', ' * Running on unix://%s/ %s', hostname, quit_msg
                )
            if use_reloader:
                if os.path.exists(hostname):
                    os.unlink(hostname)

                address_family = werkzeug.serving.select_ip_version(hostname,
                                                                    port)
                test_socket = socket.socket(address_family, socket.SOCK_STREAM)
                test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,
                                       1)
                test_socket.bind(hostname)
                test_socket.close()
                werkzeug.serving.run_with_reloader(inner, extra_files,
                                                   reloader_interval)
            else:
                inner()

        self._orig_werkzeug_serving_run_simple = werkzeug.serving.run_simple

        werkzeug.serving.run_simple = new_run_simple

    def unpatch_all(self):
        """Unpatches what needs unpatching."""
        if self._orig_werkzeug_serving_WSGIRequestHandler_init is not None:
            werkzeug.serving.WSGIRequestHandler.__init__ =\
                self._orig_werkzeug_serving_WSGIRequestHandler_init

            self._orig_werkzeug_serving_WSGIRequestHandler_init = None

        if self._orig_werkzeug_serving_select_ip_version is not None:
            werkzeug.serving.select_ip_version =\
                self._orig_werkzeug_serving_select_ip_version

        if self._orig_werkzeug_serving_BaseWSGIServer_init is not None:
            werkzeug.serving.BaseWSGIServer.__init__ =\
                self._orig_werkzeug_serving_BaseWSGIServer_init

            self._orig_werkzeug_serving_BaseWSGIServer_init = None

        if self._orig_werkzeug_serving_BaseWSGIServer_get_request is not None:
            werkzeug.serving.BaseWSGIServer.get_request =\
                self._orig_werkzeug_serving_BaseWSGIServer_get_request

            self._orig_werkzeug_serving_BaseWSGIServer_get_request = None

        if self._orig_werkzeug_serving_run_simple is not None:
            werkzeug.serving.run_simple =\
                self._orig_werkzeug_serving_run_simple

    def patch_all(self):
        """Patches what needs patching."""
        if self._orig_werkzeug_serving_WSGIRequestHandler_init is None:
            self._patch_werkzeug_serving_WSGIRequestHandler_init()

        if self._orig_werkzeug_serving_select_ip_version is None:
            self._patch_werkzeug_serving_select_ip_version()

        if self._orig_werkzeug_serving_BaseWSGIServer_init is None:
            self._patch_werkzeug_serving_BaseWSGIServer_init()

        if self._orig_werkzeug_serving_BaseWSGIServer_get_request is None:
            self._patch_werkzeug_serving_BaseWSGIServer_get_request()

        if self._orig_werkzeug_serving_run_simple is None:
            self._patch_werkzeug_serving_run_simple()

    def __call__(self):
        """Some sugar would be nice."""
        self.patch_all()

#: Pre-instantiated ``WerkzeugPatcher`` for quick use.
patch_werkzeug = WerkzeugPatcher()
