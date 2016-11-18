from __future__ import unicode_literals

from wiring.scanning import register
from yapsy.ConfigurablePluginManager import ConfigurablePluginManager
from yapsy.IPlugin import IPlugin
from yapsy.PluginManager import PluginManagerSingleton
from yapsy.VersionedPluginManager import VersionedPluginManager

from .event import connect_events, disconnect_events


class Plugin(IPlugin):
    def activate(self):
        super(Plugin, self).activate()
        connect_events(self)

    def deactivate(self):
        super(Plugin, self).deactivate()
        disconnect_events(self)


@register.function('tomate.plugin')
def provide_plugin_manager():
    PluginManagerSingleton.setBehaviour([
        ConfigurablePluginManager,
        VersionedPluginManager,
    ])

    return PluginManagerSingleton.get()
