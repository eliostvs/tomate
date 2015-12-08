from __future__ import unicode_literals

from wiring import Module, provides, scope, SingletonScope
from yapsy.IPlugin import IPlugin

from .event import Subscriber


class Plugin(Subscriber, IPlugin):
    pass


class PluginModule(Module):

    @provides('tomate.plugin')
    @scope(SingletonScope)
    def provide_plugin_manager(self):
        from yapsy.ConfigurablePluginManager import ConfigurablePluginManager
        from yapsy.PluginManager import PluginManagerSingleton
        from yapsy.VersionedPluginManager import VersionedPluginManager

        PluginManagerSingleton.setBehaviour([
            ConfigurablePluginManager,
            VersionedPluginManager,
        ])

        return PluginManagerSingleton.get()
