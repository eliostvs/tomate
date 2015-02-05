from __future__ import unicode_literals

import unittest

import six
from tomate.base import Singleton
from tomate.services import cache, LazyService, provider_service


class ServiceLocatorTestCase(unittest.TestCase):

    def _make_dummy(self):

        @provider_service('Dummy')
        @six.add_metaclass(Singleton)
        class Dummy(object):
            def foo(self):
                return 'bar'

        return Dummy()

    def test_should_only_evaluate_when_needed(self):
        dummy = self._make_dummy()
        lazy_dummy = cache.lookup('Dummy')

        self.assertIsInstance(lazy_dummy,  LazyService)
        self.assertEqual('<LazyService: (Dummy)>', str(lazy_dummy))

        self.assertEqual(None, lazy_dummy._wrapped)
        self.assertEqual('bar', lazy_dummy.foo())
        self.assertEqual(dummy, lazy_dummy._wrapped)

    def test_should_raise_a_exception_when_the_object_dont_exist(self):
        from tomate.services import ServiceNotFound

        fake = cache.lookup('Foo')

        self.assertRaises(ServiceNotFound, getattr, fake, 'foo')

    def test_should_success_when_object_is_create_after_the_proxy(self):
        lazy_dummy = cache.lookup('Dummy')
        self._make_dummy()

        self.assertEqual('bar', lazy_dummy.foo())
