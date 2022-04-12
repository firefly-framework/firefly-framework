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

from firefly.infrastructure.service import set_env
from firefly.domain.entity.core.cli_app import CliApp


@set_env
def main():
    from firefly import Kernel
    kernel = Kernel().boot()
    app = CliApp(name='firefly')
    for endpoint in kernel.get_cli_endpoints():
        app.endpoints.append(endpoint)
    kernel.argparse_executor.run(app)

# class CliOutput(ffd.Middleware):
#     def __call__(self, message: ffd.Message, next_: Callable, **kwargs) -> Optional[dict]:
#         print('CliOutput called...')
#         response = next_(message)
#
#         if isinstance(response, dict):
#             for title, data in response.items():
#                 response[title].insert(0, ('Name', 'Type'))
#                 print(SingleTable(data, title).table)
#         elif isinstance(response, list):
#             response.insert(0, ('Name', 'Type'))
#             print(SingleTable(response).table)
#
#         return response
#
#
# @ffd.cli(
#     app_name='firefly',
#     description='Firefly command line utilities',
#     middleware=[CliOutput()]
# )
# class FireflyCli:
#
#     @ffd.cli(
#         target='firefly.Deploy',
#         alias={
#             'env': 'e',
#         },
#         help_={
#             'env': 'The environment to deploy'
#         }
#     )
#     def deploy(self):
#         pass
#
#     # @ffd.cli(target='')
#     # def generate_typescript(self):
#     #     pass
