from __future__ import unicode_literals

import unittest


class IDummy(object):
    def foo():
        pass


class Dummy(IDummy):
    def foo(self):
        return 'bar'


class NonDummy(object):
    def foo(self):
        return 'bar'


class ServiceLocatorTestCase(unittest.TestCase):

    def setUp(self):
        from tomate.services import Cache
        Cache.clear()

    def test_should_fail_when_concrete_service_dont_implement_the_service_interface(self):
        from tomate.services import provider_service, ProviderError

        with self.assertRaises(ProviderError) as context:
            provider_service(IDummy)(NonDummy)()

        self.assertEqual("NonDummy doesn't implement IDummy!", context.exception.message)

    def test_should_return_the_service_object(self):
        from tomate.services import provider_service, Cache

        dummy = provider_service(interface=IDummy)(Dummy)()
        dummy_obj = Cache.get('Dummy')

        self.assertEqual(dummy, dummy_obj)

    def test_should_raise_when_the_client_not_found_the_service(self):
        from tomate.services import Cache

        with self.assertRaises(KeyError) as ctx:
            fail = Cache.get('Dummy')
            fail.foo()

        self.assertEqual('Dummy', ctx.exception.message)

    def test_should_success_when_the_service_is_create_after_the_lazy_service(self):
        from tomate.services import provider_service, Cache, LazyObject
        lazy = Cache.get('Dummy')

        self.assertIsInstance(lazy,  LazyObject)
        self.assertEqual('<LazyObject: (Dummy)>', str(lazy))

        self.assertEqual(None, lazy._wrapped)

        provider_service(IDummy)(Dummy)()

        self.assertEqual('bar', lazy.foo())
