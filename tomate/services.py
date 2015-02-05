from __future__ import unicode_literals

import logging

logger = logging.getLogger(__name__)


class ProviderError(Exception):
    pass


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


def provider_service(interface):
    def _decorator(cls):
        if not issubclass(cls, interface):
            raise ProviderError("%s doesn't implement %s!" %
                                (cls.__name__, interface.__name__))

        def _wrapped(*args, **kwargs):
            service = cls.__name__

            if service not in Cache:
                instance = cls(*args, **kwargs)
                Cache.setdefault(service, instance)

            else:
                instance = Cache[service]

                if not isinstance(instance, cls):
                    raise ProviderError('Service %s is already provided by %s' %
                                        (service, instance.__class__.__name__))

            return instance

        return _wrapped
    return _decorator
