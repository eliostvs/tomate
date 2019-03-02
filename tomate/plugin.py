import logging

from wiring import SingletonScope, inject
from wiring.scanning import register
from yapsy.ConfigurablePluginManager import ConfigurablePluginManager
from yapsy.IPlugin import IPlugin
from yapsy.PluginManager import PluginManagerSingleton
from yapsy.VersionedPluginManager import VersionedPluginManager

from tomate.config import Config
from .event import connect_events, disconnect_events

logger = logging.getLogger(__name__)


class Plugin(IPlugin):
    has_settings = False

    def activate(self):
        super(Plugin, self).activate()
        connect_events(self)

    def deactivate(self):
        super(Plugin, self).deactivate()
        disconnect_events(self)

    def settings_window(self):
        pass


@register.factory("tomate.plugin", scope=SingletonScope)
class PluginManager:
    @inject(config="tomate.config")
    def __init__(self, config: Config):
        PluginManagerSingleton.setBehaviour(
            [ConfigurablePluginManager, VersionedPluginManager]
        )

        self._plugin_manager = PluginManagerSingleton.get()
        self._plugin_manager.setPluginPlaces(config.get_plugin_paths())
        self._plugin_manager.setPluginInfoExtension("plugin")
        self._plugin_manager.setConfigParser(config.parser, config.save)

    def __getattr__(self, attr):
        logger.debug("action=getattr attr=%s", attr)
        try:
            return getattr(self._plugin_manager, attr)
        except KeyError:
            raise AttributeError(attr)
