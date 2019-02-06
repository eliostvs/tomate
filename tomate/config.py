import configparser
import logging
import os
from collections import namedtuple

from wiring import inject, SingletonScope
from wiring.scanning import register
from xdg import BaseDirectory, IconTheme

logger = logging.getLogger(__name__)

DEFAULTS = {
    "pomodoro_duration": "25",
    "shortbreak_duration": "5",
    "longbreak_duration": "15",
    "long_break_interval": "4",
}

CONFIG_PARSER = configparser.RawConfigParser(defaults=DEFAULTS, strict=True)

register.instance("config.parser")(CONFIG_PARSER)

SettingsPayload = namedtuple("SettingsPayload", "action section option value")


@register.factory("tomate.config", scope=SingletonScope)
class Config(object):
    app_name = "tomate"

    @inject(parser="config.parser", dispatcher="tomate.events.setting")
    def __init__(self, parser, dispatcher):
        self.parser = parser
        self._dispatcher = dispatcher

        self.load()

    def load(self):
        logger.debug("action=loadConfig uri=%s", self.get_config_path())

        self.parser.read(self.get_config_path())

    def save(self):
        logger.debug("action=writeConfig uri=%s", self.get_config_path())

        with open(self.get_config_path(), "w") as f:
            self.parser.write(f)

    def get_config_path(self):
        BaseDirectory.save_config_path(self.app_name)
        return os.path.join(
            BaseDirectory.xdg_config_home, self.app_name, self.app_name + ".conf"
        )

    def get_media_uri(self, *resources):
        return "file://" + self.get_resource_path(self.app_name, "media", *resources)

    def get_plugin_paths(self):
        return self.get_resource_paths(self.app_name, "plugins")

    def get_icon_paths(self):
        return self.get_resource_paths("icons")

    def get_resource_path(self, *resources):
        for resource in self.get_resource_paths(*resources):
            if os.path.exists(resource):
                return resource

            logger.debug("action=resourceNotFound uri=%s", resource)

        raise EnvironmentError(
            "Resource with path %s not found!" % os.path.join(*resources)
        )

    @staticmethod
    def get_resource_paths(*resources):
        return [p for p in BaseDirectory.load_data_paths(*resources)]

    @staticmethod
    def get_icon_path(iconname, size=None, theme=None):
        icon_path = IconTheme.getIconPath(
            iconname, size, theme, extensions=["png", "svg", "xpm"]
        )

        if icon_path is not None:
            return icon_path

        raise EnvironmentError("Icon %s not found!" % icon_path)

    def get_int(self, section, option):
        return self.get(section, option, "getint")

    def get(self, section, option, method="get"):
        section = Config.normalize(section)
        option = Config.normalize(option)

        if not self.parser.has_section(section):
            self.parser.add_section(section)

        return getattr(self.parser, method)(section, option, fallback=None)

    def set(self, section, option, value):
        section = Config.normalize(section)
        option = Config.normalize(option)

        logger.debug(
            "action=setOption section=%s option=%s value=%s", section, option, value
        )

        if not self.parser.has_section(section):
            self.parser.add_section(section)

        self.parser.set(section, option, value)

        self.save()

        payload = SettingsPayload(
            action="set", section=section, option=option, value=value
        )

        self._dispatcher.send(section, payload=payload)

    def remove(self, section, option):
        section = Config.normalize(section)
        option = Config.normalize(option)

        logger.debug("action=removeOption section=%s option=%s", section, option)

        if self.parser.has_section(section):
            self.parser.remove_option(section, option)

        self.save()

        payload = SettingsPayload(
            action="remove", section=section, option=option, value=None
        )

        self._dispatcher.send(section, payload=payload)

    @staticmethod
    def normalize(name):
        return name.replace(" ", "_").lower()
