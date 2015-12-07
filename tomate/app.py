from __future__ import unicode_literals

import dbus.service
from wiring import inject

from .enums import State


class Application(dbus.service.Object):

    bus_name = 'com.github.Tomate'
    bus_object_path = '/'
    bus_interface_name = 'com.github.Tomate'
    specifiation = 'tomate.app'

    @inject(bus='dbus.session',
            view='tomate.view',
            config='tomate.config',
            plugin='tomate.plugin')
    def __init__(self, bus, view, config, plugin):
        dbus.service.Object.__init__(self, bus, self.bus_object_path)
        self.state = State.stopped
        self.config = config
        self.view = view
        self.plugin = plugin

        self.__setup_plugin_manager()

    def __setup_plugin_manager(self):
        self.plugin.setPluginPlaces(self.config.get_plugin_paths())
        self.plugin.setPluginInfoExtension('plugin')
        self.plugin.setConfigParser(self.config.parser, self.config.save)
        self.plugin.collectPlugins()

    @dbus.service.method(bus_interface_name, out_signature='b')
    def is_running(self):
        return self.state == State.running

    @dbus.service.method(bus_interface_name, out_signature='b')
    def run(self):
        if self.is_running():
            self.view.show()

        else:
            self.state = State.running
            self.view.run()
            self.state = State.stopped

        return True

    @classmethod
    def fromgraph(cls, graph):
        bus_session = dbus.SessionBus()
        request = bus_session.request_name(cls.bus_name, dbus.bus.NAME_FLAG_DO_NOT_QUEUE)

        if request != dbus.bus.REQUEST_NAME_REPLY_EXISTS:
            graph.register_instance('dbus.session', bus_session)
            instance = graph.get(cls.specifiation)

        else:
            bus_object = bus_session.get_object(cls.bus_name, cls.bus_object_path)
            instance = dbus.Interface(bus_object, cls.bus_interface_name)

        return instance
