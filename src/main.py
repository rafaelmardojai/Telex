# main.py
#
# Copyright 2019 Rafael Mardojai CM
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import asyncio
import gbulb
import inspect
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Handy', '0.0')
from gi.repository import GObject, GLib, Gio, Gdk, Gtk, Handy, Notify

from telethon import events

from .client import TelexClient
from .settings import TelexSettings

from .app_actions import TelexApplicationActions
from .window import TelexWindow
from .preferences_window import TelexPreferencesWindow
from .contacts_dialog import ContactsDialog

def connect_async(self, detailed_signal, handler_async, *args):
    def handler(self, *args):
        asyncio.ensure_future(handler_async(self, *args))
    self.connect(detailed_signal, handler, *args)

GObject.GObject.connect_async = connect_async

class Application(Gtk.Application, TelexApplicationActions):
    def __init__(self, client):
        super().__init__(application_id='com.rafaelmardojai.Telex',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.client = client
        self.client.add_event_handler(self.notify, events.NewMessage)
        self.settings = TelexSettings.new()
        self.window = None

        TelexApplicationActions.__init__(self)

    def do_startup(self):
        Gtk.Application.do_startup(self)
        GLib.set_application_name('Telex')
        GLib.set_prgname('Telex')

        Notify.init("Telex")

        # Load CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_resource('/com/rafaelmardojai/Telex/style.css')
        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        # Register LibHandy
        GObject.type_register(Handy.Leaflet)

        # Load Settings
        settings = Gtk.Settings.get_default()

        dark = self.settings.get_value('dark-theme')
        settings.set_property('gtk-application-prefer-dark-theme', dark)
        animations = self.settings.get_value('dark-theme')
        settings.set_property('gtk-enable-animations', animations)

    def do_activate(self):
        self.window = self.props.active_window
        if not self.window:
            self.window = TelexWindow(application=self, client=self.client, settings=self.settings)
        self.window.connect('delete-event', self.on_close)
        self.window.present()

    @property
    def get_client(self):
        return self.client

def main(version):
    gbulb.install(gtk=True)

    loop = asyncio.get_event_loop()
    client = TelexClient(loop=loop)
    application = Application(client=client)

    loop.run_forever(application, sys.argv)

