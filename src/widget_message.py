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

from gi.repository import Gtk, Pango

from telethon import events, utils, types

from .widget_avatar import Avatar

class Message(Gtk.ListBoxRow):
    def __init__(self, message, sender, avatar=False, header=True, name=True):
        """
        message (Message)
        sender (sender)
        photo (bool) - Show sender avatar
        header (bool) - Show header (sender name & message date)
        """
        super().__init__()

        text = str(message.text)
        if message.media:
            text += '({}) '.format(message.media.__class__.__name__)

        Gtk.StyleContext.add_class(self.get_style_context(), 'message')
        #self.set_activatable(False)
        self.set_selectable(False)
        self.props.margin_bottom = 20

        # Main message box
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.add(box)

        if avatar:
            self.avatar = Avatar(utils.get_display_name(sender), 32)
            self.avatar.props.valign=Gtk.Align.START
            box.pack_start(self.avatar, None, None, 0)

        message_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, halign=Gtk.Align.FILL)
        box.pack_start(message_box, True, True, 0)

        if header:
            header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            if name:
                sender_name = Gtk.Label(utils.get_display_name(sender), halign=Gtk.Align.START)
                Gtk.StyleContext.add_class(sender_name.get_style_context(), 'sender-name')
                header_box.pack_start(sender_name, True, True, 0)
            time = Gtk.Label('TIME')
            Gtk.StyleContext.add_class(time.get_style_context(), 'dim-label')
            header_box.pack_end(time, None, None, 0)
            message_box.pack_start(header_box, True, None, 0)

        text_box = Gtk.Box()
        message_box.pack_start(text_box, True, True, 0)
        Gtk.StyleContext.add_class(text_box.get_style_context(), 'message-text')
        self.text = Gtk.Label(text, halign=Gtk.Align.START, xalign=0, yalign=0)
        text_box.pack_start(self.text, True, True, 0)
        self.text.set_line_wrap(True)
        self.text.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.text.set_selectable(True)

class DayPrint(Gtk.ListBoxRow):
    def __init__(self, date):
        super().__init__()

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, margin_top = 6, margin_bottom = 6)
        self.add(box)
        label = Gtk.Label(date.strftime("%m/%d/%Y"))
        Gtk.StyleContext.add_class(label.get_style_context(), 'title')

        box.pack_start(label, True, True, 0)
        self.set_selectable(False)
        self.props.margin_bottom = 20
