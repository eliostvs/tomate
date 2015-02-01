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
        from tomate.profile import ProfileManager

        self.pm = ProfileManager()

    def test_get_config_path(self, *args):
        self.assertEqual('/home/mock/.config/tomate/tomate.conf', self.pm.get_config_path())

    def test_get_plugin_path(self, *args):
        self.assertEqual(['/usr/mock/tomate/plugins'], self.pm.get_plugin_paths())

    @patch('tomate.profile.SafeConfigParser')
    def test_write_config(self, mSafeConfigParser, *args):
        from tomate.profile import ProfileManager

        pm = ProfileManager()
        mo = mock_open()

        with patch('tomate.profile.open', mo, create=True):
            pm.write_config()

        self.assertTrue(mSafeConfigParser.return_value.write.called)
        mSafeConfigParser.return_value.write.assert_called_once_with(mo())

    @patch('tomate.profile.os.path.exists', return_value=True)
    def test_get_media_file(self, mpath, *args):
        from tomate.profile import ProfileManager

        pm = ProfileManager()

        self.assertEqual('file:///usr/mock/tomate/media/alarm.mp3', pm.get_media_uri('alarm.mp3'))

    @patch('tomate.profile.os.path.exists', return_value=True)
    def test_get_help_uri(self, mpath, *args):
        from tomate.profile import ProfileManager

        pm = ProfileManager()

        self.assertEqual('ghelp:/usr/mock/help/C/tomate', pm.get_ghelp_uri())

    def test_get_resource_path_should_raise_exception(self, *args):
        self.assertRaises(EnvironmentError, self.pm.get_resource_path, '/file/not/exist/')

    @patch('tomate.profile.IconTheme.getIconPath', return_value=None)
    def test_get_icon_path_should_raise_exception(self, mgetIconPath, *args):
        self.assertRaises(EnvironmentError, self.pm.get_icon_path, 'tomate', 22)

    @patch('tomate.profile.IconTheme.getIconPath', spec_set=True)
    def test_get_icon_path_should_success(self, mgetIconPath, *args):
        from tomate.profile import ProfileManager

        mgetIconPath.side_effect = (
            lambda name, size, theme, extensions:
            '/usr/mock/icons/hicolor/{size}x{size}/apps/{name}.png'
            .format(name=name, size=size)
        )

        pm = ProfileManager()

        self.assertEqual('/usr/mock/icons/hicolor/22x22/apps/tomate.png',
                         pm.get_icon_path('tomate', 22))

    def test_icon_paths_should_success(self, *args):
        self.assertEqual(['/usr/mock/icons'], self.pm.get_icon_paths())

    @patch('tomate.profile.SafeConfigParser', spec_set=True)
    def test_get_option(self, mSafeConfigParser, *args):
        from tomate.profile import ProfileManager

        mSafeConfigParser.return_value.has_section.return_value = False
        mSafeConfigParser.return_value.has_option.return_value = False
        mSafeConfigParser.return_value.get.return_value = '25'
        mSafeConfigParser.return_value.getint.return_value = 25

        pm = ProfileManager()
        pm.write_config = Mock()

        self.assertEqual(25, pm.get_int('Timer', 'pomodoro duration'))

        mSafeConfigParser.return_value.has_section.assert_called_once_with('timer')

        mSafeConfigParser.return_value.add_section.assert_called_once_with('timer')

        mSafeConfigParser.return_value.has_option.assert_called_once_with('timer', 'pomodoro_duration')

        mSafeConfigParser.return_value.get.assert_called_once_with('timer', 'pomodoro_duration')

        mSafeConfigParser.return_value.set.assert_called_once_with('timer', 'pomodoro_duration', '25')

        pm.write_config.assert_called_once_with()

    @patch('tomate.profile.SafeConfigParser', spec_set=True)
    def test_get_methods(self, mSafeConfigParser, *args):
        from tomate.profile import ProfileManager

        pm = ProfileManager()

        pm.get('section', 'option', type=str)
        mSafeConfigParser.return_value.get.assert_called_with('section', 'option')

        pm.get_int('section', 'option')
        mSafeConfigParser.return_value.getint.assert_called_with('section', 'option')

        pm.get('section', 'option', type=bool)
        mSafeConfigParser.return_value.getboolean.assert_called_with('section', 'option')

        pm.get('section', 'option', type=float)
        mSafeConfigParser.return_value.getfloat.assert_called_with('section', 'option')

        pm.get('section', 'option', type=object)
        mSafeConfigParser.return_value.get.assert_called_with('section', 'option')

    @patch('tomate.profile.SafeConfigParser', spec_set=True)
    def test_set_option(self, mSafeConfigParser, mBaseDirectory):
        from tomate.profile import ProfileManager

        mSafeConfigParser.return_value.has_section.return_value = False

        pm = ProfileManager()
        pm.write_config = Mock()

        pm.set('Timer', 'Shortbreak Duration', 4)

        mSafeConfigParser.return_value.has_section.assert_called_once_with('timer')
        mSafeConfigParser.return_value.add_section.assert_called_once_with('timer')
        mSafeConfigParser.return_value.set.assert_called_once_with('timer', 'shortbreak_duration', 4)

        pm.write_config.assert_called_once_with()


class ProfileManagerSingletonTestCase(unittest.TestCase):

    def setUp(self):
        from tomate import profile

        reload(profile)

    def test_instance_should_be_none_on_start(self):
        from tomate.profile import ProfileManagerSingleton

        self.assertEqual(None, ProfileManagerSingleton._ProfileManagerSingleton__instance)

    def test_instance_should_be_a_profile_manager_instance(self):
        from tomate.profile import ProfileManager, ProfileManagerSingleton

        ProfileManagerSingleton.get()

        self.assertIsInstance(ProfileManagerSingleton._ProfileManagerSingleton__instance,
                              ProfileManager)

    def test_create_another_pm_instance_should_raise_a_exception(self):
        from tomate.profile import ProfileManagerSingleton

        ProfileManagerSingleton.get()

        self.assertRaises(Exception, ProfileManagerSingleton)
