from __future__ import unicode_literals

import os
import unittest

from mock import Mock, mock_open, patch

BaseDirectory_attrs = {
    'xdg_config_home': '/home/mock/.config',
    'load_data_paths.side_effect': lambda *args: [os.path.join('/usr/mock/', *args)],
}


@patch('tomate.profile.BaseDirectory', spec_set=True, **BaseDirectory_attrs)
class ProfileManagerTestCase(unittest.TestCase):

    def setUp(self):
        from tomate.config import Config

        self.pm = Config()

    def test_get_config_path(self, *args):
        self.assertEqual('/home/mock/.config/tomate/tomate.conf', self.pm.get_config_path())

    def test_get_plugin_path(self, *args):
        self.assertEqual(['/usr/mock/tomate/plugins'], self.pm.get_plugin_paths())

    def test_write_config(self, *args):
        from tomate.config import Config

        pm = Config()
        pm.config_parser = Mock()
        mo = mock_open()

        with patch('tomate.profile.open', mo, create=True):
            pm.write_config()

        self.assertTrue(pm.config_parser.write.called)
        pm.config_parser.write.assert_called_once_with(mo())

    @patch('tomate.profile.os.path.exists', return_value=True)
    def test_get_media_file(self, mpath, *args):
        from tomate.config import Config

        pm = Config()

        self.assertEqual('file:///usr/mock/tomate/media/alarm.mp3', pm.get_media_uri('alarm.mp3'))

    @patch('tomate.profile.os.path.exists', return_value=True)
    def test_get_help_uri(self, mpath, *args):
        from tomate.config import Config

        pm = Config()

        self.assertEqual('ghelp:/usr/mock/help/C/tomate', pm.get_ghelp_uri())

    def test_get_resource_path_should_raise_exception(self, *args):
        self.assertRaises(EnvironmentError, self.pm.get_resource_path, '/file/not/exist/')

    @patch('tomate.profile.IconTheme.getIconPath', return_value=None)
    def test_get_icon_path_should_raise_exception(self, mgetIconPath, *args):
        self.assertRaises(EnvironmentError, self.pm.get_icon_path, 'tomate', 22)

    @patch('tomate.profile.IconTheme.getIconPath', spec_set=True)
    def test_get_icon_path_should_success(self, mgetIconPath, *args):
        from tomate.config import Config

        mgetIconPath.side_effect = (
            lambda name, size, theme, extensions:
            '/usr/mock/icons/hicolor/{size}x{size}/apps/{name}.png'
            .format(name=name, size=size)
        )

        pm = Config()

        self.assertEqual('/usr/mock/icons/hicolor/22x22/apps/tomate.png',
                         pm.get_icon_path('tomate', 22))

    def test_icon_paths_should_success(self, *args):
        self.assertEqual(['/usr/mock/icons'], self.pm.get_icon_paths())

    def makeProfileA(self):
        from tomate.config import Config
        return Config()

    def makeProfileB(self):
        from tomate.config import Config
        return Config()

    def test_singleton(self, *args):
        instanceA = self.makeProfileA()
        instanceB = self.makeProfileB()

        self.assertEqual(instanceA, instanceB)


@patch('tomate.profile.BaseDirectory', spec_set=True, **BaseDirectory_attrs)
class TestProfileManagerReadWriteOptions(unittest.TestCase):

    def test_get_option(self, *args):
        from tomate.config import Config

        pm = Config()
        pm.write_config = Mock()
        pm.config_parser = Mock()
        pm.config_parser.has_section.return_value = False
        pm.config_parser.has_option.return_value = False
        pm.config_parser.get.return_value = '25'
        pm.config_parser.getint.return_value = 25

        self.assertEqual(25, pm.get_int('Timer', 'pomodoro duration'))

        pm.config_parser.has_section.assert_called_once_with('timer')

        pm.config_parser.add_section.assert_called_once_with('timer')

        pm.config_parser.has_option.assert_called_once_with('timer', 'pomodoro_duration')

        pm.config_parser.get.assert_called_once_with('timer', 'pomodoro_duration')

        pm.config_parser.set.assert_called_once_with('timer', 'pomodoro_duration', '25')

        pm.write_config.assert_called_once_with()

    def test_get_options(self, *args):
        from tomate.config import Config

        pm = Config()
        pm.config_parser = Mock()

        pm.get('section', 'option', type=str)
        pm.config_parser.get.assert_called_with('section', 'option')

        pm.get_int('section', 'option')
        pm.config_parser.getint.assert_called_with('section', 'option')

        pm.get('section', 'option', type=bool)
        pm.config_parser.getboolean.assert_called_with('section', 'option')

        pm.get('section', 'option', type=float)
        pm.config_parser.getfloat.assert_called_with('section', 'option')

        pm.get('section', 'option', type=object)
        pm.config_parser.get.assert_called_with('section', 'option')

    def test_set_option(self, *args):
        from tomate.config import Config

        pm = Config()
        pm.config_parser = Mock()
        pm.write_config = Mock()
        pm.config_parser.has_section.return_value = False

        pm.set('Timer', 'Shortbreak Duration', 4)

        pm.config_parser.has_section.assert_called_once_with('timer')
        pm.config_parser.add_section.assert_called_once_with('timer')
        pm.config_parser.set.assert_called_once_with('timer', 'shortbreak_duration', 4)

        pm.write_config.assert_called_once_with()
