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
from datetime import datetime, timedelta
from gi.repository import Gtk, GLib, Notify

from telethon import events, utils, types
from telethon.errors import SessionPasswordNeededError, PasswordHashInvalidError, PhoneNumberUnoccupiedError, PhoneNumberInvalidError

from .widget_avatar import Avatar
from .widget_dialog import Dialog
from .widget_message import Message, DayPrint

@Gtk.Template(resource_path='/com/rafaelmardojai/Telex/window.ui')
class TelexWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'TelexWindow'

    main_stack = Gtk.Template.Child()
    header_stack = Gtk.Template.Child()

    connection_failed = Gtk.Template.Child()

    # General
    user_btn = Gtk.Template.Child()
    user_btn_box = Gtk.Template.Child()
    me_name = Gtk.Template.Child()
    me_phone = Gtk.Template.Child()

    quit_menu_box = Gtk.Template.Child()

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

    left_header = Gtk.Template.Child()
    right_header = Gtk.Template.Child()

    header_dialog_stack = Gtk.Template.Child()
    header_dialog_box = Gtk.Template.Child()
    header_dialog_name = Gtk.Template.Child()
    header_dialog_info = Gtk.Template.Child()

    dialogs_stack = Gtk.Template.Child()
    dialogs_side_stack = Gtk.Template.Child()
    dialogs_list = Gtk.Template.Child()
    messages_log = Gtk.Template.Child()
    messages_scrolled = Gtk.Template.Child()

    def __init__(self, client, settings, **kwargs):
        super().__init__(**kwargs)

        self.client = client
        self.settings = settings

        self.first = True
        self.code = None
        self.password = None
        self.singup = None

        self.setup_btn.connect_async('clicked', self.sign_in)
        self.setup_entry.connect_async('activate', self.sign_in)
        self.singup_btn.connect_async('clicked', self.sign_in)
        self.dark_switch.set_state(self.settings.get_value('dark-theme'))

        if self.settings.get_value('run-background'):
            self.quit_menu_box.props.visible = True

        self.header_dialog_image = Avatar('', 32)
        self.header_dialog_box.pack_start(self.header_dialog_image, None, True, 0)

        self.client.loop.create_task(self.post_init())

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

        while not self.client.is_connected():
            try:
                await self.client.connect()
            except Exception as e:
                print('Failed to connect', e, file=sys.stderr)
                self.connection_failed.props.visible = True # Show error message on startup
                await asyncio.sleep(0.5)

        self.first = False
        self.client.loop.create_task(self.check_update())

        self.client.add_event_handler(self.on_message, events.NewMessage)
        if await self.client.is_user_authorized():
            self.set_signed_in(await self.client.get_me())
        else:
            self.main_stack.set_visible_child_name('setup')
            self.setup_stack.set_visible_child_name('entry')

    async def on_message(self, event):
        Notify.init("App Name")
        Notify.Notification.new("Hi").show()

    async def check_update(self):
        star = 0
        while True:
            if not self.client.is_connected():
                try:
                    print('Conecting again...')
                    await self.client.connect()
                except Exception as e:
                    print('Failed to connect', e, file=sys.stderr)
            print('Checking' + str(star))
            star += 1
            await asyncio.sleep(1)


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

    async def load_dialogs(self):
        dialogs = await self.client.get_dialogs()

        for dialog in dialogs:
            dialog_row = Dialog(dialog)
            self.dialogs_list.add(dialog_row)

        self.dialogs_side_stack.set_visible_child_name('list')
        self.dialogs_list.connect_async("row-selected", self.load_messages)

    async def load_messages(self, list, row):
        if not row:
            return

        self.info_text = ''
        self.show_avatar = False
        self.show_header = True
        self.show_name = True
        self.from_id = None
        self.date = datetime.today()

        if row.dialog.is_group:
            self.show_avatar = True
        if row.dialog.is_channel:
            self.show_name = False
        if row.dialog.is_group or row.dialog.is_channel:
            self.info_text = 'Members: ' + str(row.entity.participants_count)
        elif row.dialog.is_user:
            self.info_text = 'Last seen: '

        self.content_leaflet.set_visible_child_name('dialog-pane')
        self.dialogs_stack.set_visible_child_name('loading')
        self.header_dialog_stack.set_visible_child_name('loading')

        children = self.messages_log.get_children()
        for child in children:
            self.messages_log.remove(child)

        for message in reversed(await self.client.get_messages(row.entity, 100)):
            if self.from_id == message.from_id:
                self.show_header = False
                self.show_avatar = False
            self.from_id = message.from_id

            if self.date.date() < message.date.date():
                day = DayPrint(message.date)
                self.messages_log.add(day)
                self.show_header = True

            minutes_date = self.date + timedelta(minutes=10)
            if minutes_date.date() < message.date.date():
                self.show_header = True

            self.date = message.date

            sender = await message.get_sender()
            msg = Message(message, sender, self.show_avatar, self.show_header, self.show_name)
            self.messages_log.add(msg)

            self.show_header = True
            if row.dialog.is_group:
                self.show_avatar = True

        self.messages_log.show_all()
        adjustment = self.messages_scrolled.get_vadjustment()
        adjustment.set_value(adjustment.get_upper())

        self.header_dialog_name.set_text(row.dialog.name)
        self.header_dialog_info.set_text(self.info_text)
        self.header_dialog_image.change_avatar(row.dialog.name)

        self.header_dialog_stack.set_visible_child_name('dialog')
        self.dialogs_stack.set_visible_child_name('messages')

    @Gtk.Template.Callback()
    def _back_to_dialogs(self, widget):
        self.content_leaflet.set_visible_child_name('list-pane')
        self.dialogs_list.unselect_all()
        if not self.content_leaflet.props.folded:
            self.dialogs_stack.set_visible_child_name('select')
            self.header_dialog_stack.set_visible_child_name('select')

    @Gtk.Template.Callback()
    def _on_headerbar_folded_changed(self, leaflet, folded):

        if self.header_leaflet.props.folded:
            Gtk.StyleContext.remove_class(self.right_header.get_style_context(), 'flat-headerbar')
        else:
            Gtk.StyleContext.add_class(self.right_header.get_style_context(), 'flat-headerbar')

        if not self.dialogs_list.get_selected_row():
            self.dialogs_stack.set_visible_child_name('select')
            self.header_dialog_stack.set_visible_child_name('select')

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

