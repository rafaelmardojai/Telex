# setup_window.py
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

from gi.repository import Gtk

from telethon import utils
from telethon.errors import PhoneCodeInvalidError, SessionPasswordNeededError, PasswordHashInvalidError, PhoneNumberUnoccupiedError, PhoneNumberInvalidError

class TelexSetupWindow:
    def __init__(self):
        self.code = None
        self.builder = dialog = Gtk.Builder.new_from_resource(
            '/com/rafaelmardojai/Telex/setup-window.ui')

        self.setup_header = self.builder.get_object('setup_header')
        self.setup  = self.builder.get_object('setup')

        self.header_stack.add_named(self.setup_header, 'setup')
        self.main_stack.add_named(self.setup, 'setup')

        # Get all Setup widgets
        # -> Header buttons
        self.phone_next = self.builder.get_object('phone_next')
        self.back_phone = self.builder.get_object('back_phone')
        self.code_next = self.builder.get_object('code_next')
        self.pass_next = self.builder.get_object('pass_next')
        # -> Spinners
        self.phone_spinner = self.builder.get_object('phone_spinner')
        self.code_spinner = self.builder.get_object('code_spinner')
        self.pass_spinner = self.builder.get_object('pass_spinner')
        self.singup_spinner = self.builder.get_object('singup_spinner')
        # -> Entries
        self.phone_entry = self.builder.get_object('phone_entry')
        self.code_entry = self.builder.get_object('code_entry')
        self.pass_entry = self.builder.get_object('pass_entry')
        self.name1_entry = self.builder.get_object('name1_entry')
        self.name2_entry = self.builder.get_object('name2_entry')
        # -> Error
        self.phone_error = self.builder.get_object('phone_error')
        self.code_error = self.builder.get_object('code_error')
        self.pass_error = self.builder.get_object('pass_error')
        self.singup_error = self.builder.get_object('singup_error')
        # -> Buttons
        self.start_btn = self.builder.get_object('start_btn')
        self.singup_btn = self.builder.get_object('singup_btn')

    def start(self):
        self.header_stack.set_visible_child_name('setup')
        self.main_stack.set_visible_child_name('setup')

        self.start_btn.connect('clicked', self.start_setup)
        #self.setup.set_visible_child_name('welcome')

    def start_setup(self, widget):
        self.setup.set_visible_child_name('phone')

        self.phone_entry.connect_async('activate', self.setup_phone)
        self.phone_next.connect_async('clicked', self.setup_phone)
        self.back_phone.connect_async('clicked', self.setup_phone)

        self.code_entry.connect_async('activate', self.setup_code)
        self.code_next.connect_async('clicked', self.setup_code)

        self.pass_entry.connect_async('activate', self.setup_pass)
        self.pass_next.connect_async('clicked', self.setup_pass)

        self.singup_btn.connect_async('clicked', self.setup_singup)

    async def setup_phone(self, widget):
        self.phone_spinner.props.visible = True
        phone = self.phone_entry.get_text()

        if utils.parse_phone(phone):
            try:
                self.code = await self.client.send_code_request(phone)
                self.setup.set_visible_child_name('code')
                self.phone_spinner.props.visible = False
                return
            except PhoneNumberInvalidError:
                self.phone_error.props.visible = True
                self.phone_spinner.props.visible = False
                return
        else:
            self.phone_error.props.visible = True
            self.phone_spinner.props.visible = False
            return

    async def setup_code(self, widget):
        self.code_spinner.props.visible = True
        code = self.code_entry.get_text()

        try:
            self.set_signed_in(await self.client.sign_in(code=code))
        except PhoneCodeInvalidError:
            self.code_error.props.visible = True
            self.code_spinner.props.visible = False
            return
        except SessionPasswordNeededError:
            self.setup.set_visible_child_name('pass')
            return
        except PhoneNumberUnoccupiedError:
            self.setup.set_visible_child_name('singup')
            return

    async def setup_pass(self, widget):
        self.pass_spinner.props.visible = True
        password = self.pass_entry.get_text()

        try:
            self.set_signed_in(await self.client.sign_in(password=password))
        except PasswordHashInvalidError:
            self.pass_error.props.visible = True
            self.pass_spinner.props.visible = False
            return

    async def setup_singup(self, widget):
        self.singup_spinner.props.visible = True
        name1 = self.name1_entry.get_text()
        name2 = self.name2_entry.get_text()

        if name1:
            self.set_signed_in(await self.client.sign_up(code=self.code, first_name=name1, last_name=name2))
        else:
            self.singup_error.props.visible = True
            self.singup_spinner.props.visible = False
            return

