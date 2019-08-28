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
from gi.repository import GLib, Gio, Gtk, GdkPixbuf, Gspell

from telethon import events, utils, types

from .setup_window import TelexSetupWindow
from .widget_chat_background import ChatBackground
from .widget_avatar import Avatar
from .widget_dialog import Dialog
from .widget_message import Message, DayPrint

@Gtk.Template(resource_path='/com/rafaelmardojai/Telex/window.ui')
class TelexWindow(Gtk.ApplicationWindow, TelexSetupWindow):
    __gtype_name__ = 'TelexWindow'

    main_stack = Gtk.Template.Child()
    header_stack = Gtk.Template.Child()
    connection_failed = Gtk.Template.Child()

    # General
    me_box = Gtk.Template.Child()
    me_btn = Gtk.Template.Child()
    me_name = Gtk.Template.Child()
    me_phone = Gtk.Template.Child()

    quit_menu_box = Gtk.Template.Child()
    dark_switch = Gtk.Template.Child()

    # Chats widgets
    content_leaflet = Gtk.Template.Child()
    header_leaflet = Gtk.Template.Child()

    left_header = Gtk.Template.Child()
    right_header = Gtk.Template.Child()

    header_dialog_stack = Gtk.Template.Child()
    header_dialog_box = Gtk.Template.Child()
    header_dialog_name = Gtk.Template.Child()
    header_dialog_info = Gtk.Template.Child()

    dialogs_overlay = Gtk.Template.Child()
    dialogs_stack = Gtk.Template.Child()
    dialogs_side_stack = Gtk.Template.Child()
    dialogs_list = Gtk.Template.Child()
    messages_log = Gtk.Template.Child()
    messages_scrolled = Gtk.Template.Child()
    message_send_box = Gtk.Template.Child()
    message_input_box = Gtk.Template.Child()

    def __init__(self, client, settings, **kwargs):
        super().__init__(**kwargs)

        TelexSetupWindow.__init__(self)

        self.client = client
        self.settings = settings
        self.app = Gio.Application.get_default()
        self.selected_dialog = None

        self.dark_switch.set_state(self.settings.get_value('dark-theme'))

        if self.settings.get_value('run-background'):
            self.quit_menu_box.props.visible = True

        self.header_dialog_image = Avatar('', 32)
        self.header_dialog_box.pack_start(self.header_dialog_image, None, True, 0)

        #image = '/home/mardojai/Descargas/photo-1566632210580-97638495654a.jpg'
        #background = ChatBackground(image)
        #self.dialogs_overlay.add(background)
        self.dialogs_overlay.show_all()

        self.setup_message_entry()
        self.client.loop.create_task(self.post_init())

    def setup_message_entry(self):
        self.message_input = Gtk.TextView()
        self.message_input.set_wrap_mode(Gtk.WrapMode.WORD_CHAR);

        gspell = Gspell.TextView.get_from_gtk_text_view(self.message_input)
        gspell.basic_setup()

        scroll = Gtk.ScrolledWindow()
        self.message_input_box.pack_start(scroll, True, True, 0)
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.EXTERNAL);
        scroll.set_max_content_height(100);
        scroll.set_propagate_natural_height(True);
        scroll.add(self.message_input)

        self.message_input_box.show_all()

    async def post_init(self):
        # Connect loop
        while not self.client.is_connected():
            try:
                # Connect client
                await self.client.connect()
            except Exception as e:
                # Show connection error message
                print('Failed to connect', e, file=sys.stderr)
                self.connection_failed.props.visible = True
                await asyncio.sleep(0.5)

        #self.client.loop.create_task(self.check_update())
        self.client.add_event_handler(self.on_message, events.NewMessage)

        if await self.client.is_user_authorized():
            self.set_signed_in(await self.client.get_me())
        else:
            TelexSetupWindow.start(self)

    def set_signed_in(self, me):
        self.app.window.connect('delete-event', self.app.on_close)

        self.main_stack.set_visible_child_name('dialogs')
        self.header_stack.set_visible_child_name('dialogs')

        self.client.loop.create_task(self.load_dialogs_list())

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
        avatar = Avatar(utils.get_display_name(me), 32)
        self.me_box.pack_start(avatar, None, None, 0)

    '''async def check_update(self):
        while True:
            if not self.client.is_connected():
                try:
                    print('Conecting again...')
                    await self.client.connect()
                except Exception as e:
                    print('Failed to connect', e, file=sys.stderr)
            await asyncio.sleep(1)'''

    async def on_message(self, event):
        sender = await event.get_sender()
        notify = True
        if self.is_active():
            notify = False

        await self.load_dialogs_list()

        if event.chat_id == self.selected_dialog:
            await self.add_message(event)

        if notify:
            print('New Message!')
            notification = Gio.Notification(utils.get_display_name(sender))
            notification.set_body(event.text)
            notification.set_default_action('app.show')
            self.app.send_notification('message', notification)

    async def add_message(self, message, attach=False):
        sender = await message.get_sender()
        msg = Message(message, sender, attach)
        self.messages_log.add(msg)
        msg.show_all()

    async def load_dialogs_list(self):
        self.dialogs_side_stack.set_visible_child_name('loading')

        dialogs = await self.client.get_dialogs()
        old_dialogs = self.dialogs_list.get_children()

        for dialog in old_dialogs:
            self.dialogs_list.remove(dialog)

        for dialog in dialogs:
            dialog_row = Dialog(dialog)
            self.dialogs_list.add(dialog_row)

        self.dialogs_side_stack.set_visible_child_name('list')
        self.dialogs_list.connect_async("row-selected", self.load_dialog)

    async def load_dialog(self, list, row):
        if not row:
            return

        self.selected_dialog = row.dialog.id

        self.info_text = ''
        self.attach = False
        self.from_id = None
        self.date = datetime.today()
        self.message_send_box.props.visible = True

        if row.dialog.is_channel:
            self.message_send_box.props.visible = False
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
                self.attach = True
            self.from_id = message.from_id

            timestamp = datetime.timestamp(message.date)
            timestamp2 = datetime.timestamp(self.date) + 600
            if timestamp > timestamp2:
                self.attach = False

            if row.dialog.is_channel:
                self.attach = False

            if self.date.date() < message.date.date():
                day = DayPrint(message.date)
                self.messages_log.add(day)

            self.date = message.date

            await self.add_message(message, self.attach)

            self.attach = False

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
        self.selected_dialog = None
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

