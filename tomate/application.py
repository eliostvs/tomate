from __future__ import unicode_literals

import logging
from functools import partial

import dbus.service

from .pomodoro import Pomodoro
from .profile import ProfileManagerSingleton

logger = logging.getLogger(__name__)


class BaseApplication(dbus.service.Object):

    BUS_NAME = 'net.launchpad.tomate'
    BUS_INTERFACE_NAME = 'net.launchpad.tomate.Application'
    BUS_OBJECT_PATH = '/'
    PLUGIN_EXT = 'plugin'

    dbus_method = partial(dbus.service.method,
                          BUS_INTERFACE_NAME,
                          in_signature='',
                          out_signature='')

    def __init__(self, bus, view, **kwargs):
        dbus.service.Object.__init__(self, bus, self.BUS_OBJECT_PATH)

        self.running = False

        self.pomodoro = Pomodoro()

        self.profile = ProfileManagerSingleton.get()

        self.view = view

    @dbus_method(out_signature='b')
    def is_running(self):
        return self.running

    @dbus_method()
    def start(self, *args, **kwargs):
        if self.running:
            self.view.show_window()

        else:
            self.running = True
            self.pomodoro.change_task()
            self.view.run_window()
            self.running = False

    @dbus_method(out_signature='b')
    def exit(self, *args, **kwargs):
        if self.pomodoro.state == 'running':
            self.view.hide_window()
            return False

        else:
            self.view.delete_window()
            return True


def application_factory(application_class, view_class, **kwargs):
    bus_session = dbus.SessionBus()
    request = bus_session.request_name(application_class.BUS_NAME,
                                       dbus.bus.NAME_FLAG_DO_NOT_QUEUE)

    if request != dbus.bus.REQUEST_NAME_REPLY_EXISTS:
        app = application_class(bus_session, view=view_class, **kwargs)

    else:
        bus_object = bus_session.get_object(application_class.BUS_NAME,
                                            application_class.BUS_OBJECT_PATH)

        app = dbus.Interface(bus_object,
                             application_class.BUS_INTERFACE_NAME)

    return app
