# about.py
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

import asyncio

from gi.repository import Gtk, Handy

from telethon import functions, utils

from .widget_avatar import Avatar

@Gtk.Template(resource_path='/com/rafaelmardojai/Telex/contacts.ui')
class ContactsDialog(Handy.Dialog):
    __gtype_name__ = 'ContactsDialog'

    stack = Gtk.Template.Child()
    contacts_list = Gtk.Template.Child()

    def __init__(self, client, **kwargs):
        super().__init__(**kwargs)

        self.client = client
        self.client.loop.create_task(self.post_init())

        self.popover = Gtk.PopoverMenu()
        popoverbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.popover.add(popoverbox)

    async def post_init(self):
        result = await self.client(functions.contacts.GetContactsRequest(
            hash=0
        ))

        if len(result.users) == 0:
            self.stack.set_visible_child_name('empty')

        for user in result.users:
            row = Gtk.ListBoxRow()
            row.set_selectable(False)
            box = Gtk.Box(margin=6, spacing=10, valign=Gtk.Align.CENTER)
            row.add(box)

            avatar = Avatar(utils.get_display_name(user))
            box.pack_start(avatar, None, None, 0)

            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, halign=Gtk.Align.START)
            box.pack_start(vbox, True, True, 0)

            name = Gtk.Label(utils.get_display_name(user), halign=Gtk.Align.START)
            vbox.pack_start(name, True, True, 0)
            status = Gtk.Label('last seen', halign=Gtk.Align.START)
            Gtk.StyleContext.add_class(status.get_style_context(), 'dim-label')
            vbox.pack_start(status, True, True, 0)

            button = Gtk.MenuButton()
            icon = Gtk.Image.new_from_icon_name('view-more-symbolic', Gtk.IconSize.BUTTON)
            button.set_image(icon)
            button.set_popover(self.popover)
            button.props.valign=Gtk.Align.CENTER
            box.pack_end(button, None, None, 0)

            self.contacts_list.add(row)

        if len(result.users) > 0:
            self.contacts_list.show_all()
            self.stack.set_visible_child_name('contacts')


