from __future__ import unicode_literals

import os
import unittest

from mock import Mock, mock_open, patch

BaseDirectory_attrs = {
    'xdg_config_home': '/home/mock/.config',
    'load_data_paths.side_effect': lambda *args: [os.path.join('/usr/mock/', *args)],
}


class TestConfigInterface(unittest.TestCase):

    def test_interface(self):
        from tomate.config import IConfig, Config

        config = Config(Mock())
        IConfig.check_compliance(config)


@patch('tomate.config.BaseDirectory', spec_set=True, **BaseDirectory_attrs)
class TestConfig(unittest.TestCase):

    def setUp(self):
        from tomate.config import Config

        self.pm = Config(parser=Mock())

    def test_get_config_path(self, *args):
        self.assertEqual('/home/mock/.config/tomate/tomate.conf', self.pm.get_config_path())

    def test_get_plugin_path(self, *args):
        self.assertEqual(['/usr/mock/tomate/plugins'], self.pm.get_plugin_paths())

    def test_write_config(self, *args):
        mo = mock_open()

        with patch('tomate.config.open', mo, create=True):
            self.pm.save()

        self.assertTrue(self.pm.parser.write.called)
        self.pm.parser.write.assert_called_once_with(mo())

    @patch('tomate.config.os.path.exists', return_value=True)
    def test_get_media_file(self, mpath, *args):
        self.assertEqual('file:///usr/mock/tomate/media/alarm.mp3', self.pm.get_media_uri('alarm.mp3'))

    def test_get_resource_path_should_raise_exception(self, *args):
        self.assertRaises(EnvironmentError, self.pm.get_resource_path, '/file/not/exist/')

    @patch('tomate.config.IconTheme.getIconPath', return_value=None)
    def test_get_icon_path_should_raise_exception(self, mgetIconPath, *args):
        self.assertRaises(EnvironmentError, self.pm.get_icon_path, 'tomate', 22)

    @patch('tomate.config.IconTheme.getIconPath', spec_set=True)
    def test_get_icon_path_should_success(self, mgetIconPath, *args):
        mgetIconPath.side_effect = (
            lambda name, size, theme, extensions:
            '/usr/mock/icons/hicolor/{size}x{size}/apps/{name}.png'
            .format(name=name, size=size)
        )

        self.assertEqual('/usr/mock/icons/hicolor/22x22/apps/tomate.png',
                         self.pm.get_icon_path('tomate', 22))

    def test_icon_paths_should_success(self, *args):
        self.assertEqual(['/usr/mock/icons'], self.pm.get_icon_paths())


@patch('tomate.config.BaseDirectory', spec_set=True, **BaseDirectory_attrs)
class TestProfileManagerReadWriteOptions(unittest.TestCase):

    def setUp(self, *args):
        from tomate.config import Config

        self.pm = Config(parser=Mock())

    def test_get_option(self, *args):
        self.pm.parser.has_section.return_value = False
        self.pm.parser.has_option.return_value = False
        self.pm.parser.get.return_value = '25'
        self.pm.parser.getint.return_value = 25

        self.assertEqual(25, self.pm.get_int('Timer', 'pomodoro duration'))

        self.pm.parser.has_section.assert_called_once_with('timer')

        self.pm.parser.add_section.assert_called_once_with('timer')

        self.pm.parser.has_option.assert_called_once_with('timer', 'pomodoro_duration')

        self.pm.parser.get.assert_called_once_with('timer', 'pomodoro_duration')

        self.pm.parser.set.assert_called_once_with('timer', 'pomodoro_duration', '25')

        self.pm.save.assert_called_once_with()

    def test_get_options(self, *args):
        self.pm.get('section', 'option')
        self.pm.parser.get.assert_called_with('section', 'option')

        self.pm.get_int('section', 'option')
        self.pm.parser.getint.assert_called_with('section', 'option')

    def test_set_option(self, *args):
        self.pm.parser.has_section.return_value = False

        self.pm.set('Timer', 'Shortbreak Duration', 4)

        self.pm.parser.has_section.assert_called_once_with('timer')
        self.pm.parser.add_section.assert_called_once_with('timer')
        self.pm.parser.set.assert_called_once_with('timer', 'shortbreak_duration', 4)

        self.pm.save.assert_called_once_with()
