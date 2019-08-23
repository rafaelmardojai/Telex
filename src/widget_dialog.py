# widget_dialog.py
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

import math
import cairo
from gi.repository import Gtk, GdkPixbuf

from .widget_avatar import Avatar

@Gtk.Template(resource_path='/com/rafaelmardojai/Telex/dialogrow.ui')
class Dialog(Gtk.ListBoxRow):
    __gtype_name__ = 'DialogRow'

    box = Gtk.Template.Child()
    label_name = Gtk.Template.Child()
    label_message_time = Gtk.Template.Child()
    label_message = Gtk.Template.Child()
    icon = Gtk.Template.Child()
    pinned_icon = Gtk.Template.Child()

    def __init__(self, dialog, **kwargs):
        super().__init__(**kwargs)

        self.dialog = dialog
        self.entity = dialog.entity

        if not dialog.name:
            dialog.name = 'Deleted Account'

        self.image = Avatar(dialog.name)
        self.box.pack_start(self.image, None, None, 0)

        time = dialog.date.strftime("%m/%d/%Y")
        message = dialog.message

        text = ''
        if message.out:
            text += 'You: '
        if message.media:
            text += '({}) '.format(message.media.__class__.__name__)

        text += str(message.text).replace("\n", " ")

        if dialog.is_group or dialog.is_channel:
            self.icon.set_visible(True)
        if dialog.is_group:
            self.icon.set_from_icon_name('system-users-symbolic', Gtk.IconSize.BUTTON)
        if dialog.is_channel:
            self.icon.set_from_icon_name('user-available-symbolic', Gtk.IconSize.BUTTON)

        if dialog.pinned:
            self.pinned_icon.set_visible(True)

        self.label_name.set_text(dialog.name)
        self.label_message_time.set_text(time)
        self.label_message.set_text(text)

