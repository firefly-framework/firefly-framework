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
import json

with open('1_output.json', 'w') as fp:
    fp.write(json.dumps({'resource': '/hello-world/say-hell/Gang', 'path': '/hello-world/say-hell/Gang', 'httpMethod': 'GET', 'requestContext': {'resourcePath': '/api/hello-world/say-hell/Gang', 'httpMethod': 'GET', 'path': '/hello-world/say-hell/Gang'}, 'headers': {'accept-encoding': 'gzip', 'cache-control': 'no-cache', 'content-length': '0', 'host': 'fyyfi6211e.execute-api.us-west-2.amazonaws.com', 'pragma': 'no-cache', 'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Linux"', 'sec-fetch-dest': 'document', 'sec-fetch-mode': 'navigate', 'sec-fetch-site': 'none', 'sec-fetch-user': '?1', 'upgrade-insecure-requests': '1', 'user-agent': 'Amazon CloudFront', 'via': '2.0 de33a243d95a626772ee38d6f5849f96.cloudfront.net (CloudFront)', 'x-amz-cf-id': 'CZ3enIWRm_8zccujpqTdcHaIy_KUW4UBovN0H_ZnPO5vknayxq1DUQ==', 'x-amzn-trace-id': 'Root=1-62582e02-665ecde97291dc1e7d875093', 'x-forwarded-for': '35.161.159.188, 70.132.37.69', 'x-forwarded-port': '443', 'x-forwarded-proto': 'https'}, 'queryStringParameters': None, 'pathParameters': None, 'stageVariables': None, 'body': None, 'isBase64Encoded': False, 'multiValueQueryStringParameters': {}}))
