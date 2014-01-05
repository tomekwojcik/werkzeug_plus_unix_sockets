# -*- coding: utf-8 -*-

import codecs
from setuptools import setup

import werkzeug_unix_sock

desc_file = codecs.open('README.rst', 'r', 'utf-8')
long_description = desc_file.read()
desc_file.close()

LICENSE_URL = (
    'https://github.com/tomekwojcik/werkzeug_plus_unix_sockets/blob/'
    'master/LICENSE'
)

DESCRIPTION = (
    'Monkey-patching Werkzeug WSGI server to use Unix sockets instead of TCP '
    'sockets.'
)

setup(
    name="werkzeug_plus_unix_sockets",
    version=werkzeug_unix_sock.__version__,
    py_modules=['werkzeug_unix_sock'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Werkzeug>=0.7'
    ],
    author=u'Tomasz Wójcik'.encode('utf-8'),
    author_email='tomek@bthlabs.pl',
    maintainer=u'Tomasz Wójcik'.encode('utf-8'),
    maintainer_email='tomek@bthlabs.pl',
    url='https://github.com/tomekwojcik/werkzeug_plus_unix_sockets/',
    description=DESCRIPTION,
    long_description=long_description,
    license=LICENSE_URL
)
