# letter_avatar.py
#
# Based on avinit <https://github.com/CraveFood/avinit/>
# Copyright 2016-2019 Crave <http://cravehq.com/>
#
# Modified by Rafael Mardojai CM for Telex
# Relicensed under GPL-3.0
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

from base64 import b64encode
from xml.sax.saxutils import escape

SVG_TEMPLATE = """
<svg xmlns="http://www.w3.org/2000/svg" pointer-events="none"
     width="{width}" height="{height}">
  <rect width="{width}" height="{height}" style="{style}" rx="{radius}" ry="{radius}"></rect>
  <text text-anchor="middle" y="50%" x="50%" dy="0.35em"
        pointer-events="auto" fill="#ffffff" font-family="{font-family}"
        style="{text-style}">{text}</text>
</svg>
""".strip()
SVG_TEMPLATE = re.sub('(\s+|\n)', ' ', SVG_TEMPLATE)


def _from_dict_to_style(style_dict):
    return '; '.join(['{}: {}'.format(k, v) for k, v in style_dict.items()])


def _get_color(text):
    colors = ["#62a0ea", "#57e389", "#ffa348", "#ed333b", "#c061cb", "#b5835a",
        "#3584e4", "#33d17a", "#ff7800", "#e01b24", "#9141ac", "#986a44"]
    color_index = sum(map(ord, text)) % len(colors)
    return colors[color_index]


def get_svg_avatar(text, size):

    initials = 'DA'

    text = text.strip()
    if text:
        split_text = text.split(' ')
        if len(split_text) > 1:
            initials = split_text[0][0] + split_text[-1][0]
        else:
            initials = split_text[0][0]


    style = {
        'fill': _get_color(text),
        'width': str(size) + 'px',
        'height': str(size) + 'px',
    }

    text_style = {
        'font-weight': '400',
        'font-size': str(size / 2) + 'px',
    }

    return SVG_TEMPLATE.format(**{
        'height': str(size),
        'width': str(size),
        'style': _from_dict_to_style(style),
        'radius': str(size) + 'px',
        'font-family': 'sans-serif',
        'text-style': _from_dict_to_style(text_style),
        'text': escape(initials.upper()),
    }).replace('\n', '')


def get_avatar_data_url(text, size):
    svg_avatar = get_svg_avatar(text, size)
    b64_avatar = b64encode(svg_avatar.encode('utf-8'))
    return 'data:image/svg+xml;base64,' + b64_avatar.decode('utf-8')

