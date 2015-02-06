from __future__ import unicode_literals

import logging

logger = logging.getLogger(__name__)


class ServiceLocator(dict):

    def get(self, key, default=None):
        value = super(ServiceLocator, self).get(key, None)

        if value is None:
            value = LazyObject(key)

        return value


Cache = ServiceLocator()


class LazyObject(object):

    def __init__(self, name):
        self.name = name
        self._wrapped = None

    def __getattr__(self, func):
        if self._wrapped is None:
            self._setup()

        return getattr(self._wrapped, func)

    def _setup(self):
        self._wrapped = Cache[self.name]

    def __repr__(self):
        return '<LazyObject: (%s)>' % self.name
