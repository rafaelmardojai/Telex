# widgets.py
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
class DialogRow(Gtk.ListBoxRow):
    __gtype_name__ = 'DialogRow'

    box = Gtk.Template.Child()
    label_name = Gtk.Template.Child()
    label_message_time = Gtk.Template.Child()
    label_message = Gtk.Template.Child()

    def __init__(self, entity, name, message, message_time, image_path, **kwargs):
        super().__init__(**kwargs)

        self.entity = entity

        message_time = message_time.strftime("%m/%d/%Y")
        image = Avatar(name)

        if message is None:
            message = 'None'

        message = message.replace("\n", " ")

        self.label_name.set_text(name)
        self.label_message_time.set_text(message_time)
        self.label_message.set_text(message)

        self.box.pack_start(image, None, None, 0)
        self.box.child_set_property(image, 'position', 0)


class ProfilePhoto(Gtk.Box):
    def __init__(self, image_path, size=48, **kwargs):
        super().__init__(**kwargs)

        if image_path is None:
            image_path = '/home/mardojai/Descargas/index.png'

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(image_path, size, size, True)
        image = Gtk.Image.new_from_pixbuf(pixbuf)

        Gtk.StyleContext.add_class(self.get_style_context(), "avatar")
        self.pack_start(image, None, None, 0)
        self.show_all()

