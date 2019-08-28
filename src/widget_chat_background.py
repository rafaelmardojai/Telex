# widget_chat_background.py
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

from gi.repository import Gtk, GdkPixbuf

class ChatBackground(Gtk.Box):
    def __init__(self, image, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.layout = Gtk.Layout()
        self.pack_start(self.layout, True, True, 0)

        self.image = Gtk.Image()
        self.layout.put(self.image, 0, 0)

        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file(image)
        self.image.set_from_pixbuf(self.pixbuf)

        self.connect('size-allocate', self.on_size_allocate)

    def on_size_allocate(self, obj, rect):
        k_pixbuf = float(self.pixbuf.props.height) / self.pixbuf.props.width
        k_rect = float(rect.height) / rect.width

        # recalculate new height and width
        if k_pixbuf < k_rect:
            newHeight = rect.height
            newWidth = int(newHeight / k_pixbuf)
            coordinate = 'x'
            coordinate_reset = 'y'
            coordinate_val = -(newWidth - rect.width) // 2
        else:
            newWidth = rect.width
            newHeight = int(newWidth * k_pixbuf)
            coordinate = 'y'
            coordinate_reset = 'x'
            coordinate_val = -(newHeight - rect.height) // 2

        base_pixbuf = self.pixbuf.scale_simple(newWidth, newHeight, GdkPixbuf.InterpType.BILINEAR)
        self.image.set_from_pixbuf(base_pixbuf)

        self.layout.child_set_property(self.image, coordinate, coordinate_val)
        #self.child_set_property(self.image, coordinate, float(coordinate_val)


    '''def on_size_allocate(self, obj, rect):
        if self.pixbuf is None:
            return
        # calculate proportions for image widget and for image
        k_pixbuf = float(self.pixbuf.props.height) / self.pixbuf.props.width
        k_rect = float(rect.height) / rect.width

        # recalculate new height and width
        if k_pixbuf < k_rect:
            newWidth = rect.width
            newHeight = int(newWidth * k_pixbuf)
        else:
            newHeight = rect.height
            newWidth = int(newHeight / k_pixbuf)

        # get internal image pixbuf and check that it not yet have new sizes
        # that's allow us to avoid endless size_allocate cycle
        base_pixbuf = self.image.get_pixbuf()
        if base_pixbuf.props.height == newHeight and base_pixbuf.props.width == newWidth:
            return

        # scale image
        base_pixbuf = self.pixbuf.scale_simple(
            newWidth,
            newHeight,
            GdkPixbuf.InterpType.BILINEAR
        )

        # set internal image pixbuf to scaled image
        self.image.set_from_pixbuf(base_pixbuf)'''
        
