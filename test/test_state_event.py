from __future__ import unicode_literals

from unittest import TestCase

from mock import Mock

from tomate.event import EventState


class Foo(object):
    function = Mock()

    state = EventState('a', function, event='spam')
    other_state = EventState('b', function, '_hide')


class StateTriggerTest(TestCase):

    def test_should_return_initial_value(self):
        foo = Foo()

        self.assertEqual('a', foo.state)
        self.assertEqual('a', Foo.state)

    def test_should_has_default_attribute(self):
        foo = Foo()
        foo.state = 'a'

        self.assertTrue(hasattr(foo, '_state'))
        self.assertEqual('a', foo._state)

    def test_should_has_configurable_attribute(self):
        foo = Foo()
        foo.other_state = 'b'

        self.assertTrue(hasattr(foo, '_hide'))
        self.assertEqual(foo.other_state, foo._hide)

    def test_should_call_trigger_method_with_choosed_event_type(self):
        foo = Foo()
        foo.state = 'a'

        foo.function.assert_called_with(foo, 'spam')

    def test_should_call_trigger_method_with_default_event_type(self):
        foo = Foo()
        foo.other_state = 'b'

        foo.function.assert_called_with(foo, 'b')
