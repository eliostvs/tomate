from __future__ import unicode_literals

import logging
import weakref
from abc import ABCMeta

import six

from .base import Singleton

logger = logging.getLogger(__name__)


class ServiceNotFound(Exception):
    pass


class ServiceProviderInvalid(Exception):
    pass


@six.add_metaclass(Singleton)
class ServiceLocator(object):

    def __init__(self, *args, **kwargs):
        super(ServiceLocator, self).__init__(*args, **kwargs)
        self.__cache = weakref.WeakValueDictionary()

    def lookup(self, service):
        return LazyService(service)

    def add(self, service, instance):
        self.__cache[hash(service)] = instance

    def _lookup(self, service):
        try:
            return self.__cache[service]

        except KeyError as e:
            logger.error(e, exc_info=True)

            raise ServiceNotFound(service)


cache = ServiceLocator()


class LazyService(object):

    def __init__(self, interface):
        self._wrapped = None
        self.interface = interface

    def __getattr__(self, func):
        if self._wrapped is None:
            self._setup()

        return getattr(self._wrapped, func)

    def _setup(self):
        self._wrapped = cache._lookup(hash(self.interface))

    def __repr__(self):
        return '<LazyService: (%s)>' % self.interface.__name__


def provider_service(interface):

    def decorator(cls):
        if not issubclass(cls, interface):
            raise ServiceProviderInvalid('Class %s is not subclass of %s!' %
                                         (cls.__name__, interface.__name__))

        def wrapped(*args, **kwargs):
            instance = cls(*args, **kwargs)
            cache.add(interface, instance)
            return instance

        return wrapped
    return decorator
