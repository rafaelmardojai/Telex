# avatar.py
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

from gi.repository import GLib, Gtk, Gio, GdkPixbuf

from .letter_avatar import get_svg_avatar

class Avatar(Gtk.Box):
    def __init__(self, entity, size=48, rounded=True):
        super().__init__()

        self.size=size
        self.rounded=rounded

        #TODO use entity
        #TODO look if entity has photo

        image = get_svg_avatar(entity, size, rounded)
        loader = GdkPixbuf.PixbufLoader()
        loader.write(image.encode())
        loader.close()
        pixbuf = loader.get_pixbuf()

        self.image = Gtk.Image.new_from_pixbuf(pixbuf)
        self.pack_start(self.image, None, None, 0)

        Gtk.StyleContext.add_class(self.get_style_context(), "avatar")

        self.show_all()

    def change_avatar(self, entity):
        image = get_svg_avatar(entity, self.size, self.rounded)
        loader = GdkPixbuf.PixbufLoader()
        loader.write(image.encode())
        loader.close()
        pixbuf = loader.get_pixbuf()

        self.image.set_from_pixbuf(pixbuf)
