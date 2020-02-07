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

# __pragma__('js', '{}', "export const inflection = require('inflection');")
# __pragma__('skip')


class Inflection:
    def indexOf(self, arr: list, item, from_index: int = None, compare_func=None):
        pass

    def pluralize(self, string: str, plural: str = None):
        pass

    def singularize(self, string: str, singular: str = None):
        pass

    def inflect(self, string: str, count: int, singular: str = None, plural: str = None):
        pass

    def camelize(self, string: str, low_first_letter: bool = False):
        pass

    def underscore(self, string: str, all_upper_case: bool = False):
        pass

    def humanize(self, string: str, low_first_letter: bool = False):
        pass

    def capitalize(self, string: str):
        pass

    def dasherize(self, string: str):
        pass

    def titleize(self, string: str):
        pass

    def demodulize(self, string: str):
        pass

    def tableize(self, string: str):
        pass

    def classify(self, string: str):
        pass

    def foreign_key(self, string: str, drop_id_ubar: bool = False):
        pass

    def ordinalize(self, string: str):
        pass

    def transform(self, string: str, arr: list):
        pass


inflection = Inflection()
