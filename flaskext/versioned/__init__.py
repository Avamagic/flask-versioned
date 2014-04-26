# -*- coding: utf-8 -*-
"""
    flaskext.versioned
    ~~~~~~~~~~~~~~~~~~

    Rewrite file paths to add version info.

    :copyright: (c) 2010 by Simon Pantzare.
    :license: BSD, see LICENSE for more details
"""
import os
import time

from flask import current_app


__all__ = ['Driver', 'FileChangedDriver', 'Versioned']


class VersionedError(Exception):
    """Base error class."""
    pass


class Driver(object):
    def __init__(self, format='/version-%(version)s/%(path)s'):
        self.format = format

    def version(self, stream):
        raise NotImplementedError()


class FileChangedDriver(Driver):

    def version(self, stream):
        if not os.path.exists(stream):
            path = stream.replace(current_app.static_url_path, current_app.static_folder, 1)
            # convert to relative
            stream = stream[1:]
        else:
            path = stream

        if os.path.isabs(path):
            pass
        else:
            path = os.path.join(current_app.root_path, path)

        if not os.path.isfile(path):
            raise VersionedError("no such file: %s" % path)

        modt = time.localtime(os.path.getmtime(path))
        mods = time.strftime('%Y%m%dT%H%M%S', modt)
        return self.format % {
            'version': mods,
            'path': stream,
        }


class Versioned(object):

    def __init__(self, app=None, driver_cls=FileChangedDriver, **driver_options):
        self._driver_cls = driver_cls
        self._driver_options = driver_options
        if app is not None:
            self.init_app(app)

    def __call__(self, stream):
        return self._driver.version(stream)

    def init_app(self, app):
        self._driver = self._driver_cls(**self._driver_options)
        app.jinja_env.filters.setdefault('versioned', self)
