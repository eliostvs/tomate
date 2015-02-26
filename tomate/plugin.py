from __future__ import unicode_literals

from tomate.signals import ConnectSignalMixin
from yapsy.IPlugin import IPlugin
from yapsy.PluginManagerDecorator import PluginManagerDecorator


class TomatePluginManager(PluginManagerDecorator):

    def __init__(self,
                 decorated_manager=None,
                 categories_filter={'Default': IPlugin},
                 directories_list=None,
                 plugin_info_ext=None,
                 application=None):

        PluginManagerDecorator.__init__(self,
                                        decorated_manager,
                                        categories_filter,
                                        directories_list,
                                        plugin_info_ext)

        self.setApplication(application)

    def loadPlugins(self, callback=None):
        processed_plugins = self._component.loadPlugins(callback)

        for plugin in processed_plugins:
            plugin.plugin_object.app = self._application

        return processed_plugins

    def setApplication(self, application):
        self._application = application


class TomatePlugin(ConnectSignalMixin, IPlugin):

    def __init__(self):
        super(TomatePlugin, self).__init__()

        self.on_init()

    def activate(self):
        super(TomatePlugin, self).activate()
        self.connect_signals()
        self.on_activate()

    def deactivate(self):
        super(TomatePlugin, self).deactivate()
        self.disconnect_signals()
        self.on_deactivate()

    def on_init(self):
        pass

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass
