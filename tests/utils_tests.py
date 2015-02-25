from __future__ import unicode_literals

import unittest

from mock import patch


class FormatTimeLeftTestCase(unittest.TestCase):

    def test_format_time_left(self):
        from tomate.utils import format_time_left

        self.assertEqual('25:00', format_time_left(25 * 60))
        self.assertEqual('15:00', format_time_left(15 * 60))
        self.assertEqual('05:00', format_time_left(5 * 60))


class SupressErrorsDecoratorTestCase(unittest.TestCase):

    @patch('logging.getLogger')
    def test_suppress_errors(self, mgetLogger):
        from tomate.utils import suppress_errors

        exception = Exception('error')

        def raise_exception():
            raise exception

        self.assertEqual(None, suppress_errors(raise_exception)())

        mgetLogger.assert_called_once_with('tomate.tests.tests_utils')
        mgetLogger.return_value.error.assert_called_once_with(exception, exc_info=True)
