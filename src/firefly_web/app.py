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

from firefly.ui.web.components.layouts.default import AppContainer, MenuItem
from firefly.ui.web.js_libs.mithril import m
from firefly.ui.web.plugins import add_route, add_menu_item
from firefly.ui.web.polyfills import *  # __:skip

# __pragma__('opov')

m.route.prefix = '/admin'


def app(component):
    return AppContainer(
        component
    )


def home():
    return window.ff_menu


add_menu_item(m('div.ff-title', 'Kernel'), 0)
add_menu_item(m(MenuItem('Configuration', icon='solid/cog')), 1)
add_menu_item(m(MenuItem('System Health', icon='solid/heart')), 2)
add_menu_item(m(MenuItem('Services', icon='solid/wifi')), 3)

add_route('/', app(home()))

m.route(document.body, '/', window.ff_routes)

"""
__pragma__('js', '{}', '''
if (module.hot) {
  module.hot.accept();
}
''')
"""