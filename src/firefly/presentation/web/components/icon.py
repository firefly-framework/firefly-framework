#  Copyright (c) 2019 JD Williams
#
#  This file is part of Firefly, a Python SOA framework built by JD Williams. Firefly is free software; you can
#  redistribute it and/or modify it under the terms of the GNU General Public License as published by the
#  Free Software Foundation; either version 3 of the License, or (at your option) any later version.
#
#  Firefly is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
#  implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
#  Public License for more details. You should have received a copy of the GNU Lesser General Public
#  License along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  You should have received a copy of the GNU General Public License along with Firefly. If not, see
#  <http://www.gnu.org/licenses/>.

from firefly.presentation.web.js_libs.mithril import m
from firefly.presentation.web.polyfills import *  # __:skip

# __pragma__('kwargs')

os = None
agent = navigator.userAgent or navigator.vendor or window.opera
if 'windows phone' in agent:
    os = 'windows'
elif 'android' in agent:
    os = 'android'
elif 'iPad' in agent or 'iPhone' in agent or 'iPod' in agent:
    os = 'ios'


class Icon:
    def __init__(self, name: str, onclick=None):
        self._name = name
        self._onclick = onclick

    def view(self):
        icon = None
        name = self._name
        # __pragma__('js', '{}', "icon = require(`@fortawesome/fontawesome-free/svgs/${py_name}.svg`);")

        if self._onclick is not None:
            return m('span.cursor-pointer', {'onclick': self._onclick}, m.trust(icon))

        return m.trust(icon)
