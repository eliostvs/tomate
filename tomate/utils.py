from __future__ import unicode_literals

import functools
import logging
import os


def setup_logging(options):
    fmt = '%(levelname)s:%(asctime)s:%(name)s:%(message)s'

    if options.verbose:
        level = logging.DEBUG

    else:
        level = logging.INFO

    logging.basicConfig(level=level, format=fmt)


def format_time_left(seconds):
    minutes, seconds = divmod(seconds, 60)
    return '{0:0>2}:{1:0>2}'.format(minutes, seconds)


def suppress_errors(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)

        except Exception as e:
            logger = logging.getLogger(function.__module__)
            logger.error(e, exc_info=True)

    return wrapper


def find_xdg_data_files(install_path, topdir, pkgname, data_files=[]):
    for (dirpath, _, filenames) in os.walk(topdir):
        if filenames:
            install_path = install_path.format(pkgname=pkgname)

            subpath = dirpath.split(topdir)[1]
            if subpath.startswith('/'):
                subpath = subpath[1:]

            files = [os.path.join(dirpath, f) for f in filenames]

            data_files.append((os.path.join(install_path, subpath), files))

    return data_files


def find_data_files(data_map, pkgname):
    data_files = []

    for (system_path, local_path) in data_map:
        find_xdg_data_files(system_path, local_path, pkgname, data_files)

    return data_files


class fsm(object):

    def __init__(self, target, **kwargs):
        self.target = target
        self.source = kwargs.pop('source', '*')
        self.attr = kwargs.pop('attr', 'state')
        self.conditions = kwargs.pop('conditions', [])
        self.exit_action = kwargs.pop('exit', None)

    def valid_transition(self, instance):
        if self.source == '*' or getattr(instance, self.attr) in self.source:
            return True

    def valid_conditions(self, instance):
        if not self.conditions:
            return True

        else:
            return all(map(lambda condition: condition(instance), self.conditions))

    def change_state(self, instance):
        setattr(instance, self.attr, self.target)

    def call_exit_action(self, instance):
        if self.exit_action is not None:
            self.exit_action(instance)

    def __call__(self, method):
        @functools.wraps(method)
        def wrapper(instance, *args, **kwargs):
            if self.valid_transition(instance) and self.valid_conditions(instance):
                result = method(instance, *args, **kwargs)

                self.change_state(instance)

                self.call_exit_action(instance)

                return result

        return wrapper


class ApplicationInstanceNotFound(Exception):
    pass


class LazyApplication(object):

    def __init__(self):
        self._wrapped = None

    def __getattr__(self, func):
        if self._wrapped is None:
            self._setup()

        return getattr(self._wrapped, func)

    def _setup(self):
        from tomate.signals import app_request
        from tomate.application import Application

        for (function, instance) in app_request.send():
            if isinstance(instance, Application):
                self._wrapped = instance
                return True

        raise ApplicationInstanceNotFound
