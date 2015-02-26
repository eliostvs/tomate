from __future__ import unicode_literals

from wiring import Interface


class IView(Interface):

    visible = ''

    def run():
        pass

    def quit():
        pass

    def show():
        pass

    def hide():
        pass
