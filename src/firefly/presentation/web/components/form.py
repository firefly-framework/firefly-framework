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
from datetime import datetime, date

from firefly.presentation.web.js_libs.mithril import m
from firefly.presentation.web.js_libs.inflection import inflection
from firefly.presentation.web.js_libs.moment import moment
from firefly.presentation.web.polyfills import MissingType, ValueObject, Entity
from firefly import Validator, IsOneOf

import firefly.domain as ffd

# __pragma__('kwargs')


def form(entity: ffd.Entity, form_config: dict = None):
    dto = {}
    errors = {}
    fields = {}
    validator = Validator()
    config = {
        'placeholders': True,
        'labels': False,
        'id': 'form',
    }
    config.update(form_config or {})

    for field_ in dir(entity):
        if field_.startswith('__') or callable(getattr(entity, field_)):
            continue
        if field_ in config.get('skip', []):
            continue
        value = getattr(entity, field_)
        fields[field_] = value
        if isinstance(value, dict) and 'default_factory' in value:
            if callable(value['default_factory']):
                value = value['default_factory']()
                if isinstance(value, ffd.Empty):
                    value = ''
            else:
                value = value['default']
        if isinstance(value, (MissingType, bool)) or value is None:
            value = ''

        if field_ == 'name' and value == 'cls':
            value = ''
        dto[field_] = value

    def handle_submit(event):
        event.preventDefault()
        if 'onsubmit' in config:
            config['onsubmit'](dto)

    def get_type(f: str):
        if 'types' in config and f in config['types']:
            return config['types'][f]

        if 'metadata' in fields[f] and 'type' in fields[f]['metadata']:
            return fields[f]['metadata']['type']

        if 'metadata' in fields[f] and 'py_metatype' in fields[f]['metadata']:
            return fields[f]['metadata']['py_metatype']

        return None

    def validate():
        nonlocal errors
        e = validator.validate(dto, entity.__class__)
        if e['count'] > 0:
            errors = e['errors']

    def humanize(val: str):
        return inflection.titleize(inflection.humanize(val))

    def has_errors(f: str):
        return f in errors and len(errors[f]) > 0 and has_value(f)

    def is_required(f: str):
        return 'metadata' in fields[f] and fields[f]['metadata'].get('required', False) \
               and (not config.get('nested', False) or config.get('required', False))

    def label(f: str, conf=None):
        return f'label', m(f'label[for="{f}"].block', conf, humanize(f))

    def error_container(f: str, conf=None):
        return m(f'span[id="{f}_error"].errors', conf, error_messages(f))

    def error_messages(f: str):
        if f not in errors or not has_value(f):
            return []
        return m('ul', map(lambda msg: m('li', msg), errors[f]))

    def field_set(fields_: list, options: dict, legend: str):
        children = []
        if legend is not None:
            children.append(m('legend', legend))
        children.extend(list(map(field_group, fields_)))

        return m(f'fieldset', options, children)

    def field_group(field_: str):
        t = get_type(field_)
        nested_form = issubclass(t, (ValueObject, Entity))
        children = []
        if config['labels']:
            children.append(label(field_))

        if nested_form:
            children.append = [m(Form(t(), {'nested': True, 'required': is_required(field_)}))]
        else:
            children.append(form_field(field_))

        if nested_form is False:
            children.append(error_container(field_))

        classes = ''
        if has_errors(field_):
            classes += '.error'

        if nested_form:
            return children
        else:
            return m(f'div.field-group{classes}', children)

    def enum_fields(f: str):
        if 'metadata' in fields[f] and 'validators' in fields[f]['metadata']:
            validators = fields[f]['metadata']['validators']
        else:
            return None

        for validator in validators:
            if isinstance(validator, IsOneOf):
                values = validator.values
                if callable(values):
                    values = values(dto)
                return values

        return None

    def form_field(f: str, conf=None, children=None):
        conf = conf or {}
        if is_required(f):
            conf['required'] = 'required'

        t = get_type(f)

        def set_value(e):
            if t is bool:
                dto[f] = e.target.checked
            else:
                dto[f] = e.target.value
            validate()

        conf['oninput'] = set_value

        classes = ''
        if has_value(f) or t is bool:
            classes += '.has-value'

        if t is datetime:
            return datetime_inputs(f, classes, conf)
        elif t is date:
            return date_input(f, classes, conf)
        elif t is bool:
            return boolean_input(f, classes, conf)
        elif t is int or t is float:
            return text_input(f, classes, conf, children, input_type='number')

        values = enum_fields(f)
        if values is not None:
            return select(f, values, classes, conf)

        return text_input(f, classes, conf, children)

    def boolean_input(f: str, classes: str, conf: dict):
        if dto[f]:
            conf['checked'] = 'checked'
        return m(f'input[type="checkbox"][id="{f}"][name="{f}"].form-checkbox-input{classes}', conf)

    def text_input(f: str, classes: str, conf: dict, children, input_type: str = 'text'):
        return m(
            f'input[type="{input_type}"][id="{f}"][name="{f}"][value="{dto[f]}"][placeholder="{humanize(f)}"]'
            f'.form-text-input.px-2.py-1.rounded-sm{classes}.h-12',
            conf,
            children
        )

    def select(f: str, options, classes: str, conf: dict):
        value = dto[f]
        options = list(options)
        options.insert(0, humanize(f))

        def option(f):
            selected = ''
            if f == value:
                selected = '[selected="selected"]'
            return m(f'option[value="{f}"]{selected}', f)

        return m(f'select.form-select{classes}.h-12', conf, list(map(option, options)))

    def date_input(f: str, classes: str, conf: dict):
        return m(
            f'input[type="date"][id="{f}"][name="{f}"]'
            f'[value="{moment(dto[f]).format("YYYY-MM-DD")}"]'
            f'.form-date-input.px-2.py-1.rounded-sm.h-12{classes}',
            conf,
        )

    def datetime_inputs(f: str, classes: str, conf: dict):
        return [
            m(
                f'input[type="date"][id="{f}_date"][name="{f}_date"]'
                f'[value="{moment(dto[f]).format("YYYY-MM-DD")}"]'
                f'.form-date-input.px-2.py-1.rounded-sm.h-12{classes}',
                conf,
            ),
            m(
                f'input[type="time"][id="{f}_date"][name="{f}_date"]'
                f'[value="{moment(dto[f]).format("HH:mm")}"]'
                f'.form-time-input.px-2.py-1.rounded-sm.h-12{classes}',
                conf,
            ),
        ]

    def has_value(f: str):
        return dto[f] is not None and (not isinstance(dto[f], str) or dto[f] != '')

    def _form(conf=None, children=None):
        if 'nested' in config and config['nested']:
            return children

        return m(
            'div.form-container.flex.flex-col',
            m(
                f'form#{config["id"]}',
                conf,
                children
            )
        )

    def view():
        config = {'onsubmit': handle_submit}
        if 'fields' in config:
            keys = config['fields']
        else:
            keys = dto.keys()

        if 'exclude_fields' in config:
            keys = [x for x in keys if x not in config['exclude_fields']]

        if 'fieldsets' in config:
            form_fields = []
            for fieldset in config['fieldsets']:
                form_fields.append(
                    field_set(
                        fieldset['fields'],
                        fieldset['options'],
                        fieldset['legend'] if 'legend' in fieldset else None
                    )
                )
        else:
            form_fields = list(map(field_group, keys))

        if 'nested' not in config or not config['nested']:
            form_fields.append(m('input[type="submit"][value="Submit"].hidden.md:block'))

        return _form(config, form_fields)

    return {
        'view': view
    }


# class Form:
#     """
#     TODO
#         - Entity/VO collections
#         - Validate on submit
#         - More types? (int, float, email, phone number)...
#     """
#     def __init__(self, entity: ffd.Entity, config: dict = None):
#         self._entity = entity
#         self._dto = {}
#         self._errors = {}
#         self._config = {
#             'placeholders': True,
#             'labels': False,
#             'id': 'form',
#         }
#         self._config.update(config or {})
#         self._fields = {}
#         self._validator = Validator()
#
#         for field_ in dir(self._entity):
#             if field_.startswith('__') or callable(getattr(self._entity, field_)):
#                 continue
#             if field_ in self._config.get('skip', []):
#                 continue
#             value = getattr(self._entity, field_)
#             self._fields[field_] = value
#             if isinstance(value, dict) and 'default_factory' in value:
#                 if callable(value['default_factory']):
#                     value = value['default_factory']()
#                     if isinstance(value, ffd.Empty):
#                         value = ''
#                 else:
#                     value = value['default']
#             if isinstance(value, (MissingType, bool)) or value is None:
#                 value = ''
#
#             if field_ == 'name' and value == 'cls':
#                 value = ''
#             self._dto[field_] = value
#
#     def validate(self):
#         errors = self._validator.validate(self._dto, self._entity.__class__)
#         if errors['count'] > 0:
#             self._errors = errors['errors']
#
#     @staticmethod
#     def _wrap(component: str, vnode):
#         return vnode
#
#     @staticmethod
#     def _humanize(val: str):
#         return inflection.titleize(inflection.humanize(val))
#
#     def _has_errors(self, field_: str):
#         return field_ in self._errors and len(self._errors[field_]) > 0 and self._has_value(field_)
#
#     def _is_required(self, field_: str):
#         return 'metadata' in self._fields[field_] and self._fields[field_]['metadata'].get('required', False) \
#                and (not self._config.get('nested', False) or self._config.get('required', False))
#
#     def _form(self, config=None, children=None):
#         if 'nested' in self._config and self._config['nested']:
#             return children
#
#         return self._wrap(
#             'form',
#             m(
#                 'div.form-container.flex.flex-col',
#                 m(
#                     f'form#{self._config["id"]}',
#                     config,
#                     children
#                 )
#             )
#         )
#
#     def _field_set(self, fields: list, options: dict, legend: str):
#         children = []
#         if legend is not None:
#             children.append(m('legend', legend))
#         children.extend(list(map(self._field_group, fields)))
#
#         return self._wrap('field_set', m(f'fieldset', options, children))
#
#     def _field_group(self, field_: str):
#         t = self._get_type(field_)
#         nested_form = issubclass(t, (ValueObject, Entity))
#         children = []
#         if self._config['labels']:
#             children.append(self._label(field_))
#
#         if nested_form:
#             children.append = [m(Form(t(), {'nested': True, 'required': self._is_required(field_)}))]
#         else:
#             children.append(self._field(field_))
#
#         if nested_form is False:
#             children.append(self._error_container(field_))
#
#         classes = ''
#         if self._has_errors(field_):
#             classes += '.error'
#
#         if nested_form:
#             return self._wrap('field_group', children)
#         else:
#             return self._wrap('field_group', m(f'div.field-group{classes}', children))
#
#     def _label(self, field_: str, config=None):
#         return self._wrap(f'label', m(f'label[for="{field_}"].block', config, self._humanize(field_)))
#
#     def _error_container(self, field_: str, config=None):
#         return self._wrap('error', m(f'span[id="{field_}_error"].errors', config, self._error_messages(field_)))
#
#     def _error_messages(self, field_: str):
#         if field_ not in self._errors or not self._has_value(field_):
#             return []
#         return m('ul', map(lambda msg: m('li', msg), self._errors[field_]))
#
#     def _get_type(self, field_: str):
#         if 'types' in self._config and field_ in self._config['types']:
#             return self._config['types'][field_]
#
#         if 'metadata' in self._fields[field_] and 'type' in self._fields[field_]['metadata']:
#             return self._fields[field_]['metadata']['type']
#
#         if 'metadata' in self._fields[field_] and 'py_metatype' in self._fields[field_]['metadata']:
#             return self._fields[field_]['metadata']['py_metatype']
#
#         return None
#
#     def _enum_fields(self, field_: str):
#         if 'metadata' in self._fields[field_] and 'validators' in self._fields[field_]['metadata']:
#             validators = self._fields[field_]['metadata']['validators']
#         else:
#             return None
#
#         for validator in validators:
#             if isinstance(validator, IsOneOf):
#                 values = validator.values
#                 if callable(values):
#                     values = values(self._dto)
#                 return values
#
#         return None
#
#     def _field(self, field_: str, config=None, children=None):
#         config = config or {}
#         if self._is_required(field_):
#             config['required'] = 'required'
#
#         t = self._get_type(field_)
#
#         def set_value(e):
#             if t is bool:
#                 self._dto[field_] = e.target.checked
#             else:
#                 self._dto[field_] = e.target.value
#             self.validate()
#         config['oninput'] = set_value
#
#         classes = ''
#         if self._has_value(field_) or t is bool:
#             classes += '.has-value'
#
#         if t is datetime:
#             return self._wrap('field', self._datetime_inputs(field_, classes, config))
#         elif t is date:
#             return self._wrap('field', self._date_input(field_, classes, config))
#         elif t is bool:
#             return self._wrap('field', self._boolean_input(field_, classes, config))
#         elif t is int or t is float:
#             return self._wrap('field', self._text_input(field_, classes, config, children, input_type='number'))
#
#         values = self._enum_fields(field_)
#         if values is not None:
#             return self._wrap('field', self._select(field_, values, classes, config))
#
#         return self._wrap('field', self._text_input(field_, classes, config, children))
#
#     def _boolean_input(self, field_: str, classes: str, config: dict):
#         if self._dto[field_]:
#             config['checked'] = 'checked'
#         return m(f'input[type="checkbox"][id="{field_}"][name="{field_}"].form-checkbox-input{classes}', config)
#
#     def _text_input(self, field_: str, classes: str, config: dict, children, input_type: str = 'text'):
#         return m(
#             f'input[type="{input_type}"][id="{field_}"][name="{field_}"][value="{self._dto[field_]}"][placeholder="{self._humanize(field_)}"]'
#             f'.form-text-input.px-2.py-1.rounded-sm{classes}.h-12',
#             config,
#             children
#         )
#
#     def _select(self, field_: str, options, classes: str, config: dict):
#         value = self._dto[field_]
#         options = list(options)
#         options.insert(0, self._humanize(field_))
#
#         def option(f):
#             selected = ''
#             if f == value:
#                 selected = '[selected="selected"]'
#             return m(f'option[value="{f}"]{selected}', f)
#
#         return m(f'select.form-select{classes}.h-12', config, list(map(option, options)))
#
#     def _date_input(self, field_: str, classes: str, config: dict):
#         return m(
#             f'input[type="date"][id="{field_}"][name="{field_}"]'
#             f'[value="{moment(self._dto[field_]).format("YYYY-MM-DD")}"]'
#             f'.form-date-input.px-2.py-1.rounded-sm.h-12{classes}',
#             config,
#         )
#
#     def _datetime_inputs(self, field_: str, classes: str, config: dict):
#         return [
#             m(
#                 f'input[type="date"][id="{field_}_date"][name="{field_}_date"]'
#                 f'[value="{moment(self._dto[field_]).format("YYYY-MM-DD")}"]'
#                 f'.form-date-input.px-2.py-1.rounded-sm.h-12{classes}',
#                 config,
#             ),
#             m(
#                 f'input[type="time"][id="{field_}_date"][name="{field_}_date"]'
#                 f'[value="{moment(self._dto[field_]).format("HH:mm")}"]'
#                 f'.form-time-input.px-2.py-1.rounded-sm.h-12{classes}',
#                 config,
#             ),
#         ]
#
#     def _has_value(self, field_: str):
#         return self._dto[field_] is not None and (not isinstance(self._dto[field_], str) or self._dto[field_] != '')
#
#     def _handle_submit(self, event):
#         event.preventDefault()
#         if 'onsubmit' in self._config:
#             self._config['onsubmit'](self._dto)
#
#     def view(self):
#         config = {'onsubmit': self._handle_submit}
#         if 'fields' in self._config:
#             keys = self._config['fields']
#         else:
#             keys = self._dto.keys()
#
#         if 'exclude_fields' in self._config:
#             keys = [x for x in keys if x not in self._config['exclude_fields']]
#
#         if 'fieldsets' in self._config:
#             form_fields = []
#             for fieldset in self._config['fieldsets']:
#                 form_fields.append(
#                     self._field_set(
#                         fieldset['fields'],
#                         fieldset['options'],
#                         fieldset['legend'] if 'legend' in fieldset else None
#                     )
#                 )
#         else:
#             form_fields = list(map(self._field_group, keys))
#
#         if 'nested' not in self._config or not self._config['nested']:
#             form_fields.append(m('input[type="submit"][value="Submit"].hidden.md:block'))
#
#         return self._form(config, form_fields)
