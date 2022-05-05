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

from __future__ import annotations


class CognitoDao:
    _cognito_client = None
    _user_pool_id: str = None
    _cognito_default_client_id: str = None

    def get_clients(self):
        ret = []
        kwargs = {'UserPoolId': self._user_pool_id}
        while True:
            response = self._cognito_client.list_user_pool_clients(**kwargs)
            ret.extend(list(map(lambda x: {
                'id': x['ClientId'],
                'name': x['ClientName']
            }, response.get('UserPoolClients', []))))
            if 'NextToken' not in response:
                break
            kwargs['NextToken'] = response['TextToken']

        return ret

    def add_client(self, **kwargs):
        """
        TODO: One day we'll need this.
        """
        raise NotImplemented()
