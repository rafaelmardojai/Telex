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
from gi.repository import GObject, GLib, Gio, Gdk, Gtk, Handy

from .client import TelexClient
from .settings import TelexSettings

from .window import TelexWindow
from .preferences_window import TelexPreferencesWindow
from .contacts_dialog import ContactsDialog

def connect_async(self, detailed_signal, handler_async, *args):
    def handler(self, *args):
        asyncio.ensure_future(handler_async(self, *args))
    self.connect(detailed_signal, handler, *args)

GObject.GObject.connect_async = connect_async

class Application(Gtk.Application):
    def __init__(self, client):
        super().__init__(application_id='com.rafaelmardojai.Telex',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.client = client
        self.settings = TelexSettings.new()

    def do_startup(self):
        Gtk.Application.do_startup(self)
        GLib.set_application_name('Telex')
        GLib.set_prgname('Telex')

        # Load CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_resource('/com/rafaelmardojai/Telex/style.css')
        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        # Register LibHandy
        GObject.type_register(Handy.Leaflet)

        # App actions
        actions = [
            {
                'name': 'about',
                'func': self.on_about
            },
            {
                'name': 'shortcuts',
                'func': self.on_shortcuts
            },
            {
                'name': 'contacts',
                'func': self.on_contacts
            },
            {
                'name': 'preferences',
                'func': self.on_preferences
            },
            {
                'name': 'logout',
                'func': self.on_logout
            }
        ]

        for a in actions:
            action = Gio.SimpleAction.new(a['name'], None)
            action.connect('activate', a['func'])
            self.add_action(action)

        # Add accelerators
        self.set_accels_for_action("app.back_to_dialogs", ['<Ctrl>a'])


        # Load Settings
        settings = Gtk.Settings.get_default()

        dark = self.settings.get_value("dark-theme")
        settings.set_property("gtk-application-prefer-dark-theme", dark)

        #settings.set_property('gtk-application-prefer-dark-theme', True)

    def do_activate(self):
        self.win = self.props.active_window
        if not self.win:
            self.win = TelexWindow(application=self, client=self.client, settings=self.settings)
        self.win.present()

    def on_about(self, action, param):
        dialog = Gtk.Builder.new_from_resource(
            '/com/rafaelmardojai/Telex/about.ui'
        ).get_object('about')
        dialog.set_transient_for(self.win)
        dialog.set_modal(True)
        dialog.present()
        dialog.show_all()

    def on_shortcuts(self, action, param):
        window = Gtk.Builder.new_from_resource(
            '/com/rafaelmardojai/Telex/shortcuts.ui'
        ).get_object('shortcuts')
        window.props.section_name = 'shortcuts'
        window.set_transient_for(self.win)
        window.set_modal(True)
        window.present()
        window.show_all()

    def on_contacts(self, action, param):
        dialog = ContactsDialog()
        dialog.set_transient_for(self.win)
        dialog.set_modal(True)
        dialog.present()

    def on_preferences(self, action, param):
        window = TelexPreferencesWindow(application=self)
        window.set_transient_for(self.win)
        window.set_modal(True)
        window.present()

    def on_logout(self, action, param):
        self.client.loop.create_task(logout(self, self.client))

async def logout(app, client):
    try:
        await client.log_out()
    except Exception:
        pass

    app.quit()
    main(None)

async def quit(app, client):
    pass
    #TODO

def main(version):
    gbulb.install(gtk=True)

    loop = asyncio.get_event_loop()
    client = TelexClient(loop=loop)
    application = Application(client=client)

    loop.run_forever(application, sys.argv)

