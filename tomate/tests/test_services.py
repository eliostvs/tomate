from __future__ import unicode_literals

import unittest
from abc import ABCMeta

import six
from tomate.base import Singleton
from tomate.services import cache, LazyService, provider_service


@six.add_metaclass(ABCMeta)
class IDummy(object):
    pass


@six.add_metaclass(Singleton)
class Dummy(object):
    def foo(self):
        return 'bar'


class ServiceLocatorTestCase(unittest.TestCase):

    def test_provider_service_which_is_not_a_abc_class_should_raise(self):
        from tomate.services import ServiceProviderInvalid

        with self.assertRaises(ServiceProviderInvalid) as context:
            provider_service(object)(Dummy)()

        self.assertEqual('Class Dummy is not subclass of object!', context.exception.message)

    def test_should_only_evaluate_when_needed(self):
        dummy = provider_service(IDummy)(Dummy)()
        lazy_dummy = cache.lookup(IDummy)

        self.assertIsInstance(lazy_dummy,  LazyService)
        self.assertEqual('<LazyService: (IDummy)>', str(lazy_dummy))

        self.assertEqual(None, lazy_dummy._wrapped)
        self.assertEqual('bar', lazy_dummy.foo())
        self.assertEqual(dummy, lazy_dummy._wrapped)

    def test_should_raise_a_exception_when_the_object_dont_exist(self):
        from tomate.services import ServiceNotFound

        @six.add_metaclass(ABCMeta)
        class IFoo(object):
            pass

        fake = cache.lookup(IFoo)

        self.assertRaises(ServiceNotFound, getattr, fake, 'foo')

    def test_should_success_when_object_is_create_after_the_proxy(self):
        lazy_dummy = cache.lookup(IDummy)
        Dummy()

        self.assertEqual('bar', lazy_dummy.foo())
