# window.py
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

import sys
import asyncio
import functools
import inspect
from gi.repository import Gtk, GLib

from telethon import events, utils, types
from telethon.errors import SessionPasswordNeededError

from .widgets import DialogRow, ProfilePhoto

@Gtk.Template(resource_path='/com/rafaelmardojai/Telex/window.ui')
class TelexWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'TelexWindow'

    main_stack = Gtk.Template.Child()
    header_stack = Gtk.Template.Child()

    # General
    user_btn = Gtk.Template.Child()
    user_btn_box = Gtk.Template.Child()
    me_name = Gtk.Template.Child()
    me_phone = Gtk.Template.Child()

    dark_switch = Gtk.Template.Child()

    # Setup widgets
    setup_stack = Gtk.Template.Child()
    setup_label = Gtk.Template.Child()
    setup_entry = Gtk.Template.Child()
    setup_btn = Gtk.Template.Child()

    # Chats widgets
    content_leaflet = Gtk.Template.Child()
    header_leaflet = Gtk.Template.Child()

    dialogs_stack = Gtk.Template.Child()
    dialogs_side_stack = Gtk.Template.Child()
    dialogs_list = Gtk.Template.Child()

    def __init__(self, client, settings, **kwargs):
        super().__init__(**kwargs)

        self.client = client
        self.settings = settings

        self.code = None
        self.password = None

        #self.setup_btn.connect("clicked", self.sign_in)

        self.client.loop.create_task(self.post_init())

        self.dark_switch.set_state(self.settings.get_value("dark-theme"))

    def callback(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            loop = asyncio.get_event_loop()
            result = func(*args, **kwargs)
            if inspect.iscoroutine(result):
                loop.create_task(result)

        return wrapped

    async def post_init(self):
        await self.client.connect()

        if await self.client.is_user_authorized():
            self.set_signed_in(await self.client.get_me())
        else:
            self.main_stack.set_visible_child_name('setup')
            self.setup_stack.set_visible_child_name('entry')

    @callback
    async def sign_in(self, event=None):
        self.setup_stack.set_visible_child_name('loading')

        value = self.setup_entry.get_text()

        if self.password:
            self.setup_stack.set_visible_child_name('loading')
            self.set_signed_in(await self.client.sign_in(password=value))
        elif self.code:
            try:
                self.setup_stack.set_visible_child_name('loading')
                self.set_signed_in(await self.client.sign_in(code=value))
            except SessionPasswordNeededError:
                self.password = True
                self.setup_label.set_text('Put your cloud password')
                self.setup_entry.set_text('')
                self.setup_stack.set_visible_child_name('entry')
                return
        else:
            self.code = await self.client.send_code_request(value)
            self.setup_label.set_text('Put your confirmation code')
            self.setup_entry.set_text('')
            self.setup_stack.set_visible_child_name('entry')
            return


    def set_signed_in(self, me):
        self.main_stack.set_visible_child_name('dialogs')
        self.header_stack.set_visible_child_name('dialogs')

        self.client.loop.create_task(self.load_dialogs())

        self.me_name.set_text(utils.get_display_name(me))
        self.me_phone.set_text(utils.parse_phone(me.phone))

        """
        photo_location = me.photo.photo_small
        input_file = InputFileLocation(
            volume_id=photo_location.volume_id,
            local_id=photo_location.local_id,
            secret=photo_location.secret
        )
        file_location = os.path.join('/tmp', 'photo{}.jpg'.format(channel.id))
        self.client.download_file(input_file, file_location)
        """
        image = ProfilePhoto(None)
        self.user_btn_box.pack_start(image, None, None, 0)
        self.user_btn_box.child_set_property(image, 'position', 0)

        """self.me = me
        self.sign_in_label.configure(text='Signed in')
        self.sign_in_entry.configure(state=tkinter.NORMAL)
        self.sign_in_entry.delete(0, tkinter.END)
        self.sign_in_entry.insert(tkinter.INSERT, utils.get_display_name(me))
        self.sign_in_entry.configure(state=tkinter.DISABLED)
        self.sign_in_button.configure(text='Log out')
        self.chat.focus()
        """

    async def load_dialogs(self):
        dialogs = await self.client.get_dialogs()

        for dialog in dialogs:
            name = utils.get_display_name(dialog.entity)
            if isinstance(dialog.entity, types.User) and dialog.entity.is_self:
                name = 'Mensajes Guardados'

            message = await self.client.get_messages(dialog.entity, limit=1)
            message = message[0].text
            message_time = dialog.date
            #photo = await self.client.download_profile_photo(dialog.entity)
            photo = None

            dialog_row = DialogRow(name, message, message_time, photo)
            self.dialogs_list.add(dialog_row)
            #dialog.connect("activate", self.load_messages())

        self.dialogs_side_stack.set_visible_child_name('list')

        """async for message in client.iter_messages(chat):
            print(message.id, message.text)"""

    @Gtk.Template.Callback()
    def _on_dark_switch_state(self, widget, state):
        """
            Update view setting
            @param widget as Gtk.Switch
            @param state as bool
        """
        self.settings.set_value("dark-theme", GLib.Variant("b", state))
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme", state)

