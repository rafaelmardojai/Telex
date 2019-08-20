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
import time
import asyncio
import functools
import inspect
from gi.repository import Gtk, GLib

from telethon import events, utils, types
from telethon.errors import SessionPasswordNeededError, PasswordHashInvalidError, PhoneNumberUnoccupiedError, PhoneNumberInvalidError

from .widget_avatar import Avatar
from .widget_message import Message
from .widgets_old import DialogRow

@Gtk.Template(resource_path='/com/rafaelmardojai/Telex/window.ui')
class TelexWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'TelexWindow'

    main_stack = Gtk.Template.Child()
    header_stack = Gtk.Template.Child()
    error_label = Gtk.Template.Child()
    error_btn = Gtk.Template.Child()

    # General
    left_header = Gtk.Template.Child()
    right_header = Gtk.Template.Child()

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

    singup_btn = Gtk.Template.Child()
    singup_first = Gtk.Template.Child()
    singup_last = Gtk.Template.Child()

    # Chats widgets
    content_leaflet = Gtk.Template.Child()
    header_leaflet = Gtk.Template.Child()

    dialogs_stack = Gtk.Template.Child()
    dialogs_side_stack = Gtk.Template.Child()
    dialogs_list = Gtk.Template.Child()
    chat_log = Gtk.Template.Child()
    chat_log_scrolled = Gtk.Template.Child()

    def __init__(self, client, settings, **kwargs):
        super().__init__(**kwargs)

        self.client = client
        self.settings = settings

        self.code = None
        self.password = None
        self.singup = None

        self.setup_btn.connect_async('clicked', self.sign_in)
        self.setup_entry.connect_async('activate', self.sign_in)
        self.singup_btn.connect_async('clicked', self.sign_in)

        self.client.loop.create_task(self.post_init())

        self.dark_switch.set_state(self.settings.get_value('dark-theme'))

    """
    def callback(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            loop = asyncio.get_event_loop()
            result = func(*args, **kwargs)
            if inspect.iscoroutine(result):
                loop.create_task(result)

        return wrapped
    """

    async def post_init(self):
        try:
            await self.client.connect()
        except Exception as e:
            self.error_label.set_text('Failed to connect, try later.')
            self.error_btn.set_label('Try again')
            self.error_btn.connect_async('clicked', self.load_dialogs())

            self.main_stack.set_visible_child_name('error')
            return

        await self.client.connect()

        if await self.client.is_user_authorized():
            self.set_signed_in(await self.client.get_me())
        else:
            self.main_stack.set_visible_child_name('setup')
            self.setup_stack.set_visible_child_name('entry')

    async def sign_in(self, event=None):
        self.setup_stack.set_visible_child_name('loading')

        value = self.setup_entry.get_text()

        if not value:
            self.setup_stack.set_visible_child_name('entry')
            return

        if self.singup:
            first = self.singup_first.get_text()
            last = self.singup_last.get_text()
            self.set_signed_in(await self.client.sign_up(code=self.code, first_name=first, last_name=last))
        elif self.password:
            try:
                self.setup_stack.set_visible_child_name('loading')
                self.set_signed_in(await self.client.sign_in(password=value))
            except PasswordHashInvalidError:
                self.setup_label.set_text('Password invalid, try again')
                Gtk.StyleContext.add_class(self.setup_entry.get_style_context(), 'error')
                self.setup_stack.set_visible_child_name('entry')
                return
        elif self.code:
            try:
                self.setup_stack.set_visible_child_name('loading')
                self.set_signed_in(await self.client.sign_in(code=value))
            except SessionPasswordNeededError:
                self.password = True
                self.setup_label.set_text('Put your cloud password')
                self.setup_entry.set_text('')
                self.setup_entry.set_visibility(False)
                self.setup_stack.set_visible_child_name('entry')
                return
            except PhoneNumberUnoccupiedError:
                self.singup = True
                self.main_stack.set_visible_child_name('signup')
                return
        else:
            try:
                self.code = await self.client.send_code_request(value)
                self.setup_label.set_text('Put your confirmation code')
                self.setup_entry.set_text('')
                self.setup_stack.set_visible_child_name('entry')
                return
            except PhoneNumberInvalidError:
                self.setup_label.set_text('Phone number invalid, try again')
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
        image = Avatar(utils.get_display_name(me))
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

            dialog_row = DialogRow(dialog.entity, name, message, message_time, photo)
            self.dialogs_list.add(dialog_row)

        self.dialogs_side_stack.set_visible_child_name('list')
        self.dialogs_list.connect_async("row-selected", self.load_messages)

    def on_dialog_row_active(self, list, row):
        self.content_leaflet.set_visible_child_name('dialog-pane')
        self.dialogs_stack.set_visible_child_name('loading')

    async def load_messages(self, list, row):
        if not row:
            return

        self.content_leaflet.set_visible_child_name('dialog-pane')
        self.dialogs_stack.set_visible_child_name('loading')

        children = self.chat_log.get_children()
        for child in children:
            self.chat_log.remove(child)

        for message in await self.client.get_messages(row.entity, 20):
            sender = await message.get_sender()
            msg = Message(message.text, sender, message.out)
            self.chat_log.pack_end(msg, None, None, 0)
            self.chat_log.show_all()

        adjustment = self.chat_log_scrolled.get_vadjustment()
        adjustment.set_value(adjustment.get_upper())
        self.dialogs_stack.set_visible_child_name('chat')

    @Gtk.Template.Callback()
    def _back_to_dialogs(self, widget):
        self.content_leaflet.set_visible_child_name('list-pane')
        self.dialogs_list.unselect_all()
        if not self.content_leaflet.props.folded:
            self.dialogs_stack.set_visible_child_name('select')

    @Gtk.Template.Callback()
    def _on_headerbar_folded_changed(self, leaflet, folded):

        if self.header_leaflet.props.folded:
            Gtk.StyleContext.remove_class(self.right_header.get_style_context(), 'flat-headerbar')
        else:
            Gtk.StyleContext.add_class(self.right_header.get_style_context(), 'flat-headerbar')

        if not self.dialogs_list.get_selected_row():
            self.dialogs_stack.set_visible_child_name('select')

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

