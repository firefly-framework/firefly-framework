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

from firefly.presentation.web.bus import bus
from firefly.presentation.web.components.firefly_logo import firefly_logo
from firefly.presentation.web.components.form import Form, form
from firefly.presentation.web.components.icon import Icon
from firefly.presentation.web.js_libs.mithril import m
from firefly.presentation.web.js_libs.inflection import inflection
from firefly.presentation.web.plugins import add_route
from firefly.presentation.web.polyfills import *  # __:skip

import firefly as ff

# __pragma__('kwargs')
# __pragma__('opov')


def compose(layout, main, menu=None, header=None, drawer=None, footer=None):
    return lambda: {
        'view': layout(
            main(),
            menu() if menu is not None else None,
            header() if header is not None else None,
            drawer() if drawer is not None else None,
            footer() if footer is not None else None
        )
    }


def default_layout(main, menu, header, drawer, footer):
    drawer_is_open = False

    def close_drawer():
        nonlocal drawer_is_open
        drawer_is_open = False

    def open_drawer():
        nonlocal drawer_is_open
        drawer_is_open = True

    return lambda: [
        m('div.app.flex.flex-col', [
            m(
                'div.ff-header.fixed.flex.flex-row.justify-between.h-20.w-full.z-30.px-5.md:ml-20.md:pr-20', [
                    m('div.my-auto', m(firefly_logo)) if header is None else m(header),
                ]
            ),
            m('div.flex.flex-row', [
                m(
                    'div.ff-menu.fixed.z-30.w-full.h-20.bottom-0.flex.flex-row.justify-between'
                    '.md:left-0.md:bottom-auto.md:flex-col.md:justify-start.md:w-20.md:h-full',
                    menu or ''
                ),
                m('div.ff-content.z-0.w-full.mb-20.mt-20.flex.flex-col.justify-between'
                  '.md:ml-20.md:mb-0.md:flex-row.md:flex-wrap.md:justify-start',
                    m(main) if callable(main) or hasattr(main, 'view') else main
                )
            ]),
            m('div.ff-footer', footer) if footer is not None else '',
        ]),
        m(
            f'div.ff-drawer-bg.z-40{".open" if drawer_is_open is True else ""}',
            {'onclick': close_drawer},
            m(
                'div.ff-drawer',
                {'onclick': lambda e: e.stopPropagation()},
                m('div.flex.flex-row.h-full', [
                    m('div.w-10/12', drawer or ''),
                    m(
                        'div.w-2/12.h-full.px-1.flex.flex-col.justify-center',
                        m('div.invert-stroke.w-full.h-10', {'onclick': close_drawer}, m(Icon('solid/chevron-left')))
                    )
                ])
            )
        )
    ]


def menu_item(text, icon=None, onclick=None, route=None):
    def view():
        options = {}
        if onclick is not None:
            options['onclick'] = onclick

        item = m('div.ff-card.flex.flex-row.justify-start.h-16.md:justify-center.md:flex-col.md:w-56.md:ml-3.md:h-32', options, [
            m('div.w-8.h-full.invert-stroke.ml-2.py-3.md:ml-0.md:h-20.md:w-full.md:flex.md:flex-row.md:justify-center', m(Icon(icon))),
            m('div.w-10/12.ml-3.flex.flex-col.justify-center.md:w-full.md:ml-0.md:flex-row.md:justify-center', text),
        ])

        if route is not None:
            item = m(m.route.Link, {'href': route}, item)

        return item

    return {'view': view}


def button(data):
    style = data['style'] or 'horizontal'

    def view():
        config = {}
        if 'onclick' in data:
            config['onclick'] = data['onclick']
        elif 'route' in data:
            def redirect():
                m.route.set(data['route'])
            config['onclick'] = redirect

        content = [m('span.flex.flex-col.justify-center.font-bold', data['content'])]
        if 'left_icon' in data:
            content.insert(0, m('div.invert-stroke.my-auto.w-5.mr-2', m(Icon(data['left_icon']))))
        if 'right_icon' in data:
            content.append(m('div.invert-stroke.my-auto.w-5.ml-2', m(Icon(data['right_icon']))))

        classes = ''
        if style == 'horizontal':
            classes += '.flex.flex-row.justify-between'

        return m(f'button[type="button"]{classes}.h-10.border.rounded.px-2.my-auto', config, content)

    return {'view': view}


def crud(entity: str, cls, route_prefix: str, form_config: dict = None):
    if '.' not in entity:
        raise ff.LogicError('entity must be formatted as "<context>.<entity>"')
    parts = entity.split('.')
    context = parts[0]
    entity = parts[1]

    def crud_list():
        entities = []

        def set_entities(e):
            nonlocal entities
            entities = e
        bus.request(f'{context}.{inflection.pluralize(entity)}').then(set_entities)

        return {
            'view': lambda: m('div', list(map(lambda e: e.to_dict(), entities)))
        }

    def crud_new():
        return {
            'view': lambda: m(form(cls(), form_config))
        }

    def redirect(return_route):
        def _redirect():
            m.route.set(return_route or '/')
        return _redirect

    add_route(route_prefix, compose(default_layout, crud_list, header=lambda: {
        'view': lambda: [
            m(
                'div.w-8.invert-stroke.flex.flex-col.justify-center',
                m(Icon('solid/arrow-left', onclick=redirect('/')))
            ),
            m(button({'content': 'New', 'left_icon': 'solid/plus', 'route': f'{route_prefix}/new'}))
        ]
    }))
    
    add_route(f'{route_prefix}/new', compose(default_layout, crud_new))


class Crud:
    def __init__(self, entity: str, cls, route_prefix: str, form_config: dict = None):
        if '.' not in entity:
            raise ff.LogicError('entity must be formatted as "<context>.<entity>"')
        parts = entity.split('.')
        self._context = parts[0]
        self._entity = parts[1]
        self._class = cls
        self._route_prefix = route_prefix
        self._form_config = form_config or {}

    def routes(self):
        return {
            f'{self._route_prefix}': m(app_container, {
                'content': self._list(),
                'header_content': self._header(
                    '/',
                    m(button, {'content': 'New', 'left_icon': 'solid/plus', 'route': f'{self._route_prefix}/new'})
                ),
            }),
            f'{self._route_prefix}/:id/view': self._detail(),
            f'{self._route_prefix}/new': m(app_container, {
                'content': self._create(),
                'header_content': self._header(
                    self._route_prefix,
                    # TODO onclick save the form
                    m(button, {'content': 'Save', 'left_icon': 'solid/save'})
                )
            }),
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
        return m(Form(self._class(), self._form_config))

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
