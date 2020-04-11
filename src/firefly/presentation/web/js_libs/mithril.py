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

# __pragma__('js', '{}', "export const m = require('mithril');")
# __pragma__('js', '{}', "export const Stream = require('mithril/stream');")
# __pragma__('skip')


class Route:
    prefix = None

    def __call__(self, root, default_route, routes):
        pass

    def set(self, path):
        pass

    def get(self):
        pass


class M:
    def __init__(self):
        self.route = Route()

    def __call__(self, selector, attrs, children=None):
        pass

    def render(self):
        pass

    def mount(self, element, component):
        pass

    def request(self, options):
        pass

    def jsonp(self, options):
        pass

    def parseQueryString(self, querystring):
        pass

    def buildQueryString(self, obj):
        pass

    def trust(self, html):
        pass

    def redraw(self):
        pass


m = M()


class Stream:
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        pass

    def __getattr__(self, item):
        pass
