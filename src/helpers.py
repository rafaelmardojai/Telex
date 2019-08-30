# helpers.py
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

import re

def html_to_pango(html):
    '''
    Convert HTML tags to valid Pango tags
    '''

    # Convert <strong> to <b>
    html = re.sub(r'<(/?)strong>', r'<\1b>', html)

    # Convert <em> to <i>
    html = re.sub(r'<(/?)em>', r'<\1i>', html)

    # Convert <del> to <s>
    html = re.sub(r'<(/?)del>', r'<\1s>', html)

    # Remove <pre>
    html = re.sub(r'<(/?)pre>', '', html)

    # Convert <code> to <tt>
    html = re.sub(r'<(/?)code>', r'<\1tt>', html)

    return html
