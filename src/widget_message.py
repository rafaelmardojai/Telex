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

import re
from datetime import datetime, timezone
from gi.repository import Gtk, Pango

from telethon import events, utils, types

from .helpers import html_to_pango

from .widget_avatar import Avatar

class Message(Gtk.ListBoxRow):
    def __init__(self, message, sender, attach=False):
        """
        message (Message)
        sender (sender)
        photo (bool) - Show sender avatar
        header (bool) - Show header (sender name & message date)
        """
        super().__init__()

        self.date = message.date.replace(tzinfo=timezone.utc).astimezone(tz=None)
        text = str(message.text)
        if message.media:
            text += '({}) '.format(message.media.__class__.__name__)

        Gtk.StyleContext.add_class(self.get_style_context(), 'message')
        self.set_activatable(False)
        self.set_selectable(False)
        if not attach:
            self.props.margin_top = 6

        halign = Gtk.Align.START
        if message.out:
            halign = Gtk.Align.END

        # Main message box
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.add(box)


        self.avatar = Avatar(utils.get_display_name(sender), 32)
        self.avatar.props.valign=Gtk.Align.START
        if message.is_group and not attach:
            box.pack_start(self.avatar, None, None, 0)

        message_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, halign=halign)
        Gtk.StyleContext.add_class(message_box.get_style_context(), 'message-bubble')
        if message.out:
            Gtk.StyleContext.add_class(message_box.get_style_context(), 'message-bubble-me')
        box.pack_start(message_box, True, True, 0)
        if not message.is_channel:
            if message.out:
                message_box.props.margin_left = 40
                box.child_set_property(message_box, 'position', 0)
            else:
                message_box.props.margin_right = 40
            ...

        if not attach:
            header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, halign=halign, spacing=6)
            if not message.is_channel:
                sender_name = Gtk.Label(utils.get_display_name(sender))
                Gtk.StyleContext.add_class(sender_name.get_style_context(), 'sender-name')
                header_box.pack_start(sender_name, None, None, 0)
            time = Gtk.Label(self.date.strftime('%H:%M'))
            Gtk.StyleContext.add_class(time.get_style_context(), 'dim-label')
            header_box.pack_start(time, None, None, 0)
            if message.views:
                views = Gtk.Label(str(message.views))
                Gtk.StyleContext.add_class(time.get_style_context(), 'dim-label')
                header_box.pack_start(views, None, None, 0)
            message_box.pack_start(header_box, True, None, 0)

        text_box = Gtk.Box(halign=halign)
        message_box.pack_start(text_box, True, True, 0)

        if attach and message.is_group:
            if message.out:
                message_box.props.margin_right = 42
            else:
                message_box.props.margin_left = 42

        self.text = Gtk.Label(html_to_pango(text), halign=halign, xalign=0, yalign=0)
        self.text.set_use_markup(True)
        self.text.set_line_wrap(True)
        self.text.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.text.set_selectable(True)
        text_box.pack_start(self.text, True, True, 0)

class DayPrint(Gtk.ListBoxRow):
    def __init__(self, date):
        super().__init__()
        self.set_selectable(False)
        self.set_activatable(False)
        self.props.margin_top = 20

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, halign=Gtk.Align.CENTER, margin_top = 6, margin_bottom = 6)
        self.add(box)
        label = Gtk.Label(date.strftime("%m/%d/%Y"))
        Gtk.StyleContext.add_class(label.get_style_context(), 'day-title')

        box.pack_start(label, True, True, 0)
