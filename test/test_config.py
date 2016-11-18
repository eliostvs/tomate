from __future__ import unicode_literals

import os

import pytest
from mock import Mock, mock_open, patch

BaseDirectory_attrs = {
    'xdg_config_home': '/home/mock/.config',
    'load_data_paths.side_effect': lambda *args: [os.path.join('/usr/mock/', *args)],
}


@pytest.fixture()
def config():
    from tomate.config import Config

    return Config(Mock(), Mock())


@patch('tomate.config.BaseDirectory', spec_set=True, **BaseDirectory_attrs)
class TestConfig:
    def test_get_config_path(self, base_directory, config):
        assert config.get_config_path() == '/home/mock/.config/tomate/tomate.conf'

    def test_get_plugin_path(self, base_directory, config):
        assert config.get_plugin_paths() == ['/usr/mock/tomate/plugins']

    def test_write_config(self, base_directory, config):
        mo = mock_open()

        with patch('tomate.config.open', mo, create=True):
            config.save()

        assert config.parser.write.called

        config.parser.write.assert_called_once_with(mo())

    @patch('tomate.config.os.path.exists', spec_set=True, return_value=True)
    def test_get_media_file(self, path, base_directory, config):
        config.get_media_uri('alarm.mp3') == 'file:///usr/mock/tomate/media/alarm.mp3'

    def test_get_resource_path_should_raise_exception(self, base_directory, config):
        with pytest.raises(EnvironmentError):
            config.get_resource_path('/file/not/exist/')

    @patch('tomate.config.IconTheme.getIconPath', return_value=None)
    def test_get_icon_path_should_raise_exception(self, get_icon_path, base_directory, config):
        with pytest.raises(EnvironmentError):
            config.get_icon_path('tomate', 22)

    @patch('tomate.config.IconTheme.getIconPath', spec_set=True)
    def test_get_icon_path_should_success(self, get_icon_path, base_directory, config):
        get_icon_path.side_effect = (
            lambda name, size, theme, extensions:
            '/usr/mock/icons/hicolor/{size}x{size}/apps/{name}.png'
                .format(name=name, size=size)
        )

        assert config.get_icon_path('tomate', 22) == '/usr/mock/icons/hicolor/22x22/apps/tomate.png'

    def test_icon_paths_should_success(self, base_directory, config):
        assert config.get_icon_paths() == ['/usr/mock/icons']

    def test_get_option(self, base_directory, config):
        config.parser.has_section.return_value = False
        config.parser.has_option.return_value = False
        config.parser.get.return_value = '25'
        config.parser.getint.return_value = 25

        assert config.get_int('Timer', 'pomodoro duration') == 25

        config.parser.has_section.assert_called_once_with('timer')
        config.parser.add_section.assert_called_once_with('timer')
        config.parser.has_option.assert_called_once_with('timer', 'pomodoro_duration')
        config.parser.get.assert_called_once_with('timer', 'pomodoro_duration')
        config.parser.set.assert_called_once_with('timer', 'pomodoro_duration', '25')

    def test_get_options(self, base_directory, config):
        config.get('section', 'option')

        config.parser.get.assert_called_with('section', 'option')

        config.get_int('section', 'option')
        config.parser.getint.assert_called_with('section', 'option')

    def test_set_option(self, base_directory, config):
        config.parser.has_section.return_value = False

        mo = mock_open()

        with patch('tomate.config.open', mo, create=True):
            config.set('Timer', 'Shortbreak Duration', 4)

            config.parser.has_section.assert_called_once_with('timer')
            config.parser.add_section.assert_called_once_with('timer')
            config.parser.set.assert_called_once_with('timer', 'shortbreak_duration', 4)

            config.parser.write.assert_called_once_with(mo())


@patch('tomate.config.BaseDirectory', spec_set=True, **BaseDirectory_attrs)
def test_should_emit_setting_changed(base_directory, config):
    with patch('tomate.config.open', mock_open(), create=True):
        config.set('Timer', 'Pomodoro', 4)

        config.event.send.assert_called_once_with('timer',
                                                  section='timer',
                                                  option='pomodoro',
                                                  value=4)


def test_module(graph):
    assert 'tomate.config' in graph.providers
