from __future__ import unicode_literals

import unittest
from abc import ABCMeta, abstractmethod

import six
from tomate.base import Singleton


@six.add_metaclass(ABCMeta)
class IDummy(object):

    @abstractmethod
    def foo():
        pass


@six.add_metaclass(Singleton)
class Dummy(object):
    def foo(self):
        return 'bar'


class ServiceLocatorTestCase(unittest.TestCase):

    def setUp(self):
        from tomate.services import cache
        cache.clear()

    def test_should_fail_when_concrete_service_dont_implement_the_service_interface(self):
        from tomate.services import provider_service, ServiceProviderInvalid

        with self.assertRaises(ServiceProviderInvalid) as context:
            provider_service(IDummy)(Dummy)()

        self.assertEqual("Dummy doesn't implement IDummy!", context.exception.message)

    def test_should_lazy_evaluate_the_service(self):
        from tomate.services import provider_service, cache, LazyService

        IDummy.register(Dummy)

        dummy = provider_service(IDummy)(Dummy)()
        lazy = cache.lookup(IDummy)

        self.assertIsInstance(lazy,  LazyService)
        self.assertEqual('<LazyService: (IDummy)>', str(lazy))

        self.assertEqual(None, lazy._wrapped)
        self.assertEqual('bar', lazy.foo())
        self.assertEqual(dummy, lazy._wrapped)

    def test_should_raise_when_the_client_not_found_the_service(self):
        from tomate.services import ServiceNotFound, cache

        with self.assertRaises(ServiceNotFound) as ctx:
            fail = cache.lookup(IDummy)
            fail.foo()

        self.assertEqual('IDummy', ctx.exception.message)

    def test_should_success_when_the_service_is_create_after_the_lazy_service(self):
        from tomate.services import provider_service, cache
        lazy = cache.lookup(IDummy)

        IDummy.register(Dummy)
        provider_service(IDummy)(Dummy)()

        self.assertEqual('bar', lazy.foo())
