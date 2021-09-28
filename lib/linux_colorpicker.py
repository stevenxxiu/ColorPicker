#!/usr/bin/env python
import sys

import gi
gi.require_version('Gdk', '4.0')
gi.require_version('Gtk', '4.0')
from gi.repository import Gdk, Gtk


class ColorPicker:
    def __init__(self, init_color=None):
        self.app = None
        self.init_color = init_color

    def on_response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            # Convert to 8-bit channels
            rgba = dialog.get_rgba()
            print(f'{round(rgba.red * 255):02X}{round(rgba.green * 255):02X}{round(rgba.blue * 255):02X}')
        self.app.quit()

    def on_activate(self, app):
        window = Gtk.ApplicationWindow(application=app)
        dialog = Gtk.ColorChooserDialog.new('Sublime Color Picker')
        if self.init_color is not None:
            dialog.set_rgba(self.init_color)
        # Show the editor, otherwise we can only choose amongst a few fixed colors
        dialog.set_property('show-editor', True)
        dialog.connect('response', self.on_response)
        dialog.set_transient_for(window)
        dialog.present()

    def run(self):
        self.app = Gtk.Application()
        self.app.connect('activate', self.on_activate)
        self.app.run(None)


def main():
    init_color = None
    if len(sys.argv) > 1:
        init_color = Gdk.RGBA()
        init_color.parse(sys.argv[1])
    ColorPicker(init_color).run()


main()
