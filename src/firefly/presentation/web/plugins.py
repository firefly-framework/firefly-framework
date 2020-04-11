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

from firefly.presentation.web.components.layouts.default import Crud
from firefly.presentation.web.polyfills import *  # __:skip


def add_route(route: str, vnode):
    if 'ff_routes' not in window:
        window.ff_routes = {}

    if isinstance(vnode, Crud):
        for k, v in vnode.routes().items():
            window.ff_routes[k] = v
        # window.ff_routes.update(vnode.routes())
    else:
        window.ff_routes[route] = vnode


def add_menu_item(vnode, index: int = None):
    if 'ff_menu' not in window:
        window.ff_menu = []
    if index is None:
        window.ff_menu.append(vnode)
    else:
        window.ff_menu.insert(index, vnode)
