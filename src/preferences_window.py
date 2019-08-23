# settings_window.py
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

from gi.repository import GLib, Gtk, Handy

@Gtk.Template(resource_path='/com/rafaelmardojai/Telex/preferences.ui')
class TelexPreferencesWindow(Handy.PreferencesWindow):
    __gtype_name__ = 'TelexPreferencesWindow'

    # Get config widgets
    run_background = Gtk.Template.Child()
    close_dialog = Gtk.Template.Child()
    close_dialog_row = Gtk.Template.Child()

    animations = Gtk.Template.Child()

    def __init__(self, client, settings, app, **kwargs):
        super().__init__(**kwargs)

        self.client = client
        self.settings = settings
        self.gtk_settings = Gtk.Settings.get_default()
        self.app = app

        # Load actual config
        self.run_background.set_state(self.settings.get_value('run-background'))
        self.close_dialog.set_state(self.settings.get_value('close-dialog'))

        self.animations.set_state(self.settings.get_value('animations'))


        run_background = self.settings.get_value('run-background')
        show_dialog = self.settings.get_value('close-dialog')

        if run_background:
            self.close_dialog_row.props.visible = True

    '''
    BEHAVIOR FUNCTIONS
    '''
    @Gtk.Template.Callback()
    def _on_run_background_switch_state(self, widget, state):
        self.settings.set_value('run-background', GLib.Variant('b', state))
        if state:
            self.close_dialog_row.props.visible = True
        else:
            self.close_dialog_row.props.visible = False

    @Gtk.Template.Callback()
    def _on_close_dialog_switch_state(self, widget, state):
        self.settings.set_value('close-dialog', GLib.Variant('b', state))

    '''
    SECURITY FUNCTIONS
    '''
    @Gtk.Template.Callback()
    def _on_logout(self, widget):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING,
            Gtk.ButtonsType.YES_NO, 'Do you want to terminate this session?')
        response = dialog.run()
        if response == Gtk.ResponseType.YES:
            self.client.loop.create_task(self.__logout())

        dialog.destroy()

    async def __logout(self):
        '''
        Log out from TG
        '''
        try:
            await self.client.log_out()
        except Exception:
            pass

        self.app.quit()

    '''
    ADVANCED FUNCTIONS
    '''
    @Gtk.Template.Callback()
    def _on_animations_switch_state(self, widget, state):
        self.settings.set_value('animations', GLib.Variant('b', state))
        self.gtk_settings.set_property('gtk-enable-animations', state)

