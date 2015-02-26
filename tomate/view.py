from __future__ import unicode_literals

from wiring import Interface


class IView(Interface):

    state = ''

    def run(self):
        pass

    def quit(self):
        pass

    def show(self):
        pass

    def hide(self):
        pass
