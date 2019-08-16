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
from gi.repository import GLib, Gtk

from telethon import events, utils
from telethon.errors import SessionPasswordNeededError

from .widgets import DialogRow

@Gtk.Template(resource_path='/com/rafaelmardojai/Telex/window.ui')
class TelexWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'TelexWindow'

    main_stack = Gtk.Template.Child()
    header_stack = Gtk.Template.Child()

    # Setup widgets
    setup_stack = Gtk.Template.Child()
    setup_label = Gtk.Template.Child()
    setup_entry = Gtk.Template.Child()
    setup_btn = Gtk.Template.Child()

    # Chats widgets
    dialogs_stack = Gtk.Template.Child()
    dialogs_list = Gtk.Template.Child()

    me_name = Gtk.Template.Child()
    me_phone = Gtk.Template.Child()

    def __init__(self, client, **kwargs):
        super().__init__(**kwargs)

        self.client = client
        self.code = None
        self.password = None

        self.setup_btn.connect("clicked", self.sign_in)

        self.client.loop.create_task(self.post_init())

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
        self.me_phone.set_text(utils.get_display_name(me))

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
            #self._client.get_message_history(dialog.entity, limit=1)[0].message

            name = utils.get_display_name(dialog.entity)
            #photo = await self.client.download_profile_photo(dialog.entity)
            dialog = DialogRow(name)
            self.dialogs_list.add(dialog)
            #dialog.connect("activate", self.load_messages())
            dialog.show_all()

        async for message in client.iter_messages(chat):
            print(message.id, message.text)

