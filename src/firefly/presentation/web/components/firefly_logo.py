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


firefly_icon = {
    'view': lambda: m('div.logo-image.rounded-full', [
        m('div.firefly.one'),
        m('div.firefly.two'),
        m('div.firefly.three'),
    ])
}


firefly_logo_text = {
    'view': lambda: [
        m('span.fire.inline-block.ml-2', 'Fire'),
        m('span.fly.inline-block', 'fly')
    ]
}


firefly_logo = {
    'view': lambda: m('div.logo.font-sans.font-bold.text-shadow.rambla.flex.flex-row.justify-start', [
        m(firefly_icon),
        m(firefly_logo_text),
    ])
}
