from __future__ import unicode_literals

import logging
import os

from wiring import injects
from xdg import BaseDirectory, IconTheme

from .signals import tomate_signals

logger = logging.getLogger(__name__)

DEFAULTS = {
    'pomodoro_duration': '25',
    'shortbreak_duration': '5',
    'longbreak_duration': '15',
    'long_break_interval': '4',
}


class Config(object):

    app = 'tomate'

    @injects(config_parser='config_parser')
    def __init__(self, config_parser):
        self.config_parser = config_parser

        self.config_parser.read(self.get_config_path())

        logger.debug('reading config file %s', self.get_config_path())

    def get_plugin_paths(self):
        return self.get_resource_paths(self.app, 'plugins')

    def get_resource_paths(self, *resources):
        return [p for p in BaseDirectory.load_data_paths(*resources)]

    def get_config_path(self):
        BaseDirectory.save_config_path(self.app)
        return os.path.join(BaseDirectory.xdg_config_home, self.app, self.app + '.conf')

    def write_config(self):
        logger.debug('writing config file %s', self.get_config_path())

        with open(self.get_config_path(), 'w') as f:
            self.config_parser.write(f)

    def get_media_uri(self, *resources):
        return 'file://' + self.get_resource_path(self.app, 'media', *resources)

    def get_ghelp_uri(self, language='C'):
        return 'ghelp:' + self.get_resource_path('help', language, self.app)

    def get_resource_path(self, *resources, **kwargs):
        for resource in self.get_resource_paths(*resources):
            if os.path.exists(resource):
                return resource

            logger.debug('resource not found: %s', resource)

        raise EnvironmentError('resource with path %s not found!' % os.path.join(*resources))

    def get_icon_path(self, iconname, size=None, theme=None):
        iconpath = IconTheme.getIconPath(iconname, size, theme, extensions=['png', 'svg', 'xpm'])

        if iconpath is not None:
            return iconpath

        raise EnvironmentError('Icon %s not found!' % iconpath)

    def get_icon_paths(self):
        return self.get_resource_paths('icons')

    def get_int(self, section, option):
        return self.get(section, option, int)

    def get(self, section, option, type=str):
        section_name = section.lower()
        if not self.config_parser.has_section(section_name):
            self.config_parser.add_section(section_name)

        option_name = self._get_option_name(option)
        if not self.config_parser.has_option(section_name, option_name):
            option_value = self.config_parser.get(section_name, option_name)

            self.config_parser.set(section_name, option_name, option_value)

            self.write_config()

        return self._get_parser_method(type)(section_name, option_name)

    def _get_parser_method(self, type):
        methods = {
            str: 'get',
            int: 'getint',
            float: 'getfloat',
            bool: 'getboolean',
        }

        try:
            method = methods[type]
        except Exception:
            method = 'get'

        return getattr(self.config_parser, method)

    def _get_option_name(self, option_name):
        return option_name.replace(" ", "_").lower()

    def set(self, section, option, value):
        section_name = section.lower()
        if not self.config_parser.has_section(section_name):
            self.config_parser.add_section(section_name)

        option_name = self._get_option_name(option)
        self.config_parser.set(section_name, option_name, value)

        self.write_config()

        tomate_signals.emit('setting_changed',
                            section=section,
                            option=option,
                            value=value)

        logger.debug('Setting change: Section=%s Option=%s Value=%s',
                     section, option, value)
