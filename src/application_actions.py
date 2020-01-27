# app_actions.py
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

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Handy', '0.0')
from gi.repository import GLib, Gio, Gtk

from .client import TelexClient
from .settings import TelexSettings

from .preferences_window import TelexPreferencesWindow
from .contacts_dialog import ContactsDialog

class TelexApplicationActions:
    def __init__(self):
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
                'name': 'show',
                'func': self.on_show
            },
            {
                'name': 'quit',
                'func': self.on_quit
            }
        ]

        for a in actions:
            action = Gio.SimpleAction.new(a['name'], None)
            action.connect('activate', a['func'])
            self.add_action(action)

        # Add accelerators
        self.set_accels_for_action('app.back_to_dialogs', ['<Ctrl>a'])

    def on_show(self, action, param):
        self.window.present()

    def on_close(self, widget, event):
        background = self.settings.get_value('run-background')
        show_dialog = self.settings.get_value('close-dialog')

        if background:
            if show_dialog:
                dialog = Gtk.MessageDialog(self.window, 0, Gtk.MessageType.WARNING,
                    Gtk.ButtonsType.YES_NO, 'Closing')
                dialog.format_secondary_text(
                    'Do you want to keep Telex in background?')

                check = Gtk.CheckButton(_('Remember my decision'))
                check.props.halign = Gtk.Align.CENTER
                check.show()
                dialog.vbox.pack_start(check, True, True, 0)

                response = dialog.run()
                if check.get_active():
                    self.settings.set_value('close-dialog', GLib.Variant('b', False))
                if response == Gtk.ResponseType.YES:
                    dialog.destroy()
                    return widget.hide_on_delete()
                if response == Gtk.ResponseType.NO:
                    if check.get_active():
                        self.settings.set_value('run-background', GLib.Variant('b', False))
                    self.on_quit()
            else:
                return widget.hide_on_delete()
        else:
            self.on_quit()

    def on_quit(self, action=None, param=None):
        self.client.loop.create_task(self.__quit())

    async def __quit(self):
        try:
            await self.client.disconnect()
        except Exception:
            pass

        self.quit()

    def on_about(self, action, param):
        dialog = Gtk.Builder.new_from_resource(
            '/com/rafaelmardojai/Telex/about.ui'
        ).get_object('about')
        dialog.set_transient_for(self.window)
        dialog.set_modal(True)
        dialog.present()
        dialog.show_all()

    def on_shortcuts(self, action, param):
        window = Gtk.Builder.new_from_resource(
            '/com/rafaelmardojai/Telex/shortcuts.ui'
        ).get_object('shortcuts')
        window.set_transient_for(self.window)
        window.props.section_name = 'shortcuts'
        window.set_modal(True)
        window.present()
        window.show_all()

    def on_contacts(self, action, param):
        dialog = ContactsDialog(self.client, self.window)
        dialog.set_transient_for(self.window)
        dialog.set_modal(True)
        dialog.present()

    def on_preferences(self, action, param):
        window = TelexPreferencesWindow(self.client, self.settings, self, application=self)
        window.set_transient_for(self.window)
        window.set_modal(True)
        window.present()

