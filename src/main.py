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
import gi
import asyncio
import gbulb

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

from .client import TelexClient

from .window import TelexWindow
from .about import AboutDialog

class Application(Gtk.Application):
    def __init__(self, client):
        super().__init__(application_id='com.rafaelmardojai.Telex',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.client = client

        """
        App actions
        """
        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)

        """
        App Settings
        """
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme", True)

    def do_activate(self):
        self.win = self.props.active_window
        if not self.win:
            self.win = TelexWindow(application=self, client=self.client)
        self.win.present()

    def on_about(self, action, param):
        about_dialog = AboutDialog()
        about_dialog.set_transient_for(self.win)
        about_dialog.set_modal(True)
        about_dialog.present()

def main(version):
    gbulb.install(gtk=True)

    loop = asyncio.get_event_loop()
    client = TelexClient(loop=loop)

    loop.run_forever(application=Application(client=client))

