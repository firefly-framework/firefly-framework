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

from firefly.ui.web.bus import bus
from firefly.ui.web.components.firefly_logo import FireflyLogo
from firefly.ui.web.components.form import Form
from firefly.ui.web.components.icon import Icon
from firefly.ui.web.js_libs.mithril import m
from firefly.ui.web.js_libs.inflection import inflection
from firefly.ui.web.polyfills import *  # __:skip

import firefly as ff

# __pragma__('kwargs')
# __pragma__('opov')


class AppContainer:
    def __init__(self, content, drawer_content=None, menu_content=None, footer_content=None, header_content=None):
        default_header_content = [
            m('div.my-auto', m(FireflyLogo())),
        ]
        if drawer_content is not None:
            default_header_content.append(
                m('div.w-10.h-10.my-auto.mr-3.invert-stroke', m(Icon('solid/bars', onclick=self._open_drawer)))
            )

        self._header = Header(header_content or default_header_content)
        self._drawer = Drawer(drawer_content or [])
        self._menu = MainMenu(menu_content or [
            m('div', '')
        ])
        self._main_content = MainContent(content)
        self._footer = Footer(footer_content)

    def _open_drawer(self):
        self._drawer.is_open = True

    def view(self):
        return [
            m('div.app.flex.flex-col', [
                m(self._header),
                m('div.flex.flex-row', [
                    m(self._menu),
                    m(self._main_content),
                ]),
                m(self._footer),
            ]),
            m(self._drawer),
        ]


class Drawer:
    def __init__(self, content):
        self._content = content
        self.is_open = False

    def _close(self):
        self.is_open = False

    def view(self):
        cls = '.open' if self.is_open is True else ''
        return m(
            f'div.ff-drawer-bg.z-40{cls}',
            {'onclick': self._close},
            m(
                'div.ff-drawer',
                {'onclick': lambda e: e.stopPropagation()},
                m('div.flex.flex-row.h-full', [
                    m('div.w-10/12', self._content),
                    m(
                        'div.w-2/12.h-full.px-1.flex.flex-col.justify-center',
                        m('div.invert-stroke.w-full.h-10', {'onclick': self._close}, m(Icon('solid/chevron-left')))
                    )
                ])
            )
        )


class Header:
    def __init__(self, content):
        self._content = content

    def view(self):
        return m(
            'div.ff-header.fixed.flex.flex-row.justify-between.h-20.w-full.z-30.px-5'
            '.md:ml-20',
            self._content
        )


class MainMenu:
    def __init__(self, content=None):
        self._content = content or []

    def view(self):
        return m(
            'div.ff-menu.fixed.z-30.w-full.h-20.bottom-0.flex.flex-row.justify-between'
            '.md:left-0.md:bottom-auto.md:flex-col.md:justify-start.md:w-20.md:h-full',
            self._content
        )


class MainContent:
    def __init__(self, content):
        self._content = content

    def view(self):
        return m(
            'div.ff-content.z-0.w-full.mb-20.mt-20.flex.flex-col.justify-between'
            '.md:ml-20.md:mb-0.md:flex-row.md:flex-wrap.md:justify-start',
            self._content
        )


class Footer:
    def __init__(self, content):
        self._content = content

    def view(self):
        return m('div.ff-footer', self._content) if self._content is not None else None


class MenuItem:
    def __init__(self, text: str, onclick=None, route=None, icon=None):
        self._text = text
        self._onclick = onclick
        self._route = route
        self._icon = icon

    def view(self):
        options = {}
        if self._onclick is not None:
            options['onclick'] = self._onclick

        item = m('div.ff-card.flex.flex-row.justify-start.h-16.md:justify-center.md:flex-col.md:w-56.md:ml-3.md:h-32', options, [
            m('div.w-8.h-full.invert-stroke.ml-2.py-3.md:ml-0.md:h-20.md:w-full.md:flex.md:flex-row.md:justify-center', m(Icon(self._icon))),
            m('div.w-10/12.ml-3.flex.flex-col.justify-center.md:w-full.md:ml-0.md:flex-row.md:justify-center', self._text),
        ])

        if self._route is not None:
            item = m(m.route.Link, {'href': self._route}, item)

        return item


class Button:
    def __init__(self, content, left_icon=None, right_icon=None, onclick=None, route=None, style='horizontal'):
        self._content = content
        self._left_icon = left_icon
        self._right_icon = right_icon
        self._onclick = onclick
        self._route = route
        self._style = style

    def view(self):
        config = {}
        if self._onclick is not None:
            config['onclick'] = self._onclick
        elif self._route is not None:
            def redirect():
                m.route.set(self._route)
            config['onclick'] = redirect

        content = [m('span.flex.flex-col.justify-center.font-bold', self._content)]
        if self._left_icon is not None:
            content.insert(0, m('div.invert-stroke.my-auto.w-5.mr-2', m(Icon(self._left_icon))))
        if self._right_icon is not None:
            content.append(m('div.invert-stroke.my-auto.w-5.ml-2', m(Icon(self._right_icon))))

        classes = ''
        if self._style == 'horizontal':
            classes += '.flex.flex-row.justify-between'

        return m(f'button[type="button"]{classes}.h-10.border.rounded.px-2.my-auto', config, content)


class Crud:
    def __init__(self, entity: str, cls, route_prefix: str):
        if '.' not in entity:
            raise ff.LogicError('entity must be formatted as "<context>.<entity>"')
        parts = entity.split('.')
        self._context = parts[0]
        self._entity = parts[1]
        self._class = cls
        self._route_prefix = route_prefix

    def routes(self):
        return {
            f'{self._route_prefix}': AppContainer(
                self._list(),
                header_content=self._header(
                    '/',
                    m(Button('New', left_icon='solid/plus', route=f'{self._route_prefix}/new'))
                )
            ),
            f'{self._route_prefix}/:id/view': self._detail(),
            f'{self._route_prefix}/new': AppContainer(
                self._create(),
                header_content=self._header(
                    self._route_prefix,
                    # TODO onclick save the form
                    m(Button('Save', left_icon='solid/save'))
                )
            ),
        }

    def _header(self, return_route, right_button):
        def redirect():
            m.route.set(return_route or '/')

        return [
            m(
                'div.w-8.invert-stroke.flex.flex-col.justify-center',
                m(Icon('solid/arrow-left', onclick=redirect))
            ),
            right_button,
        ]

    def _detail(self):
        pass

    def _create(self):
        return m(Form(self._class()))

    def _list(self):
        context = self._context
        entity = self._entity
        entities = []

        class ListEntity:
            @staticmethod
            def oninit():
                def set_entities(e):
                    nonlocal entities
                    entities = e
                    m.redraw()
                # TODO Use a QueryStream
                bus.request(f'{context}.{inflection.pluralize(entity)}').then(set_entities)

            @staticmethod
            def view():
                return m('div', list(map(lambda e: e.to_dict(), entities)))

        return m(ListEntity())
