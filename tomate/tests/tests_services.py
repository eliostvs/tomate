from __future__ import unicode_literals

import unittest


class Dummy(object):
    def foo(self):
        return 'foo'


class ServiceLocatorTestCase(unittest.TestCase):

    def setUp(self):
        from tomate.services import Cache
        Cache.clear()

    def test_should_return_the_object(self):
        from tomate.services import Cache

        dummy = Dummy()
        Cache.setdefault('Dummy', dummy)

        self.assertEqual(dummy, Cache.lookup('Dummy'))

    def test_should_return_a_lazy_object(self):
        from tomate.services import Cache, LazyObject

        lazy = Cache.lookup('Dummy')

        self.assertIsInstance(lazy,  LazyObject)
        self.assertEqual('<LazyObject: (Dummy)>', str(lazy))

        self.assertEqual(None, lazy._wrapped)

        dummy = Dummy()
        Cache.setdefault('Dummy', dummy)

        self.assertEqual(None, lazy._wrapped)
        self.assertEqual('foo', lazy.foo())
        self.assertEqual(dummy, lazy._wrapped)

    def test_should_raise_keyerror_exception(self):
        from tomate.services import Cache

        with self.assertRaises(KeyError) as ctx:
            fail = Cache.lookup('Dummy')
            fail.foo()

        self.assertEqual('Dummy', ctx.exception.message)
