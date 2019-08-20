# widget_message.py
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

from gi.repository import Gtk

from telethon import events, utils, types

from .widget_avatar import Avatar

class Message(Gtk.Box):
    def __init__(self, text, sender, me):
        super().__init__()
        self.props.halign = Gtk.Align.START
        self.props.spacing = 6

        avatar = Avatar(utils.get_display_name(sender), 32)
        if me:
            self.pack_end(avatar, None, None, 0)
            self.props.halign = Gtk.Align.END
        else:
            self.pack_start(avatar, None, None, 0)

        message_buble = Gtk.Box()
        self.pack_start(message_buble, True, None, 0)
        Gtk.StyleContext.add_class(message_buble.get_style_context(), "message")

        self.text = Gtk.Label(text)
        message_buble.pack_start(self.text, None, None, 0)
        self.text.set_line_wrap(True)
        self.text.set_selectable(True)
        self.text.props.halign = Gtk.Align.START

