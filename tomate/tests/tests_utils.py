from __future__ import unicode_literals

import unittest

from mock import Mock, patch


class FormatTimeLeftTestCase(unittest.TestCase):

    def test_should_format_seconds_to_string(self):
        from tomate.utils import format_time_left

        self.assertEqual('25:00', format_time_left(25 * 60))
        self.assertEqual('15:00', format_time_left(15 * 60))
        self.assertEqual('05:00', format_time_left(5 * 60))


class SetupLoginTestCase(unittest.TestCase):

    @patch('logging.basicConfig')
    def test_should_set_level_debug(self, mBasicConfig):
        import logging
        from tomate.utils import setup_logging

        options = Mock()
        options.verbose = True

        setup_logging(options)

        mBasicConfig.assert_called_once_with(level=logging.DEBUG, format='%(levelname)s:%(asctime)s:%(name)s:%(message)s')

    @patch('logging.basicConfig')
    def test_should_set_level_info(self, mBasicConfig):
        import logging
        from tomate.utils import setup_logging

        options = Mock()
        options.verbose = None

        setup_logging(options)

        mBasicConfig.assert_called_once_with(level=logging.INFO, format='%(levelname)s:%(asctime)s:%(name)s:%(message)s')


class SupressErrorsDecoratorTestCase(unittest.TestCase):

    @patch('logging.getLogger')
    def test_should_logger_exception_without_return_error(self, mgetLogger):
        from tomate.utils import suppress_errors

        exception = Exception('error')

        def raise_exception():
            raise exception

        self.assertEqual(None, suppress_errors(raise_exception)())

        mgetLogger.assert_called_once_with('tomate.tests.tests_utils')
        mgetLogger.return_value.error.assert_called_once_with(exception, exc_info=True)
