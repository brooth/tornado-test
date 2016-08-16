# pylint: disable=locally-disabled, invalid-name
"""
Main testing module
"""

import os
import logging

from datetime import datetime, timedelta

import tornado.web
import tornado.testing

from tornado.options import options, parse_command_line

options.logging = None
parse_command_line()

logger = logging.getLogger()
app = None


class UnitTest(tornado.testing.AsyncHTTPTestCase):
    """
    base unit test
    """
    async def fetch(self, uri, **kwargs):
        if not kwargs:
            kwargs = {}
        kwargs['raise_error'] = False
        return await self.http_client.fetch(self.get_url(uri), **kwargs)

    def get_app(self):
        logger.debug('get_app()')
        if not app:
            create_app()

        return app

    def setUp(self):
        logger.debug('setUp()')
        super().setUp()

    def tearDown(self):
        logger.debug('tearDown()')
        from app.model import model
        model.client.drop_database('tornado-test-test')
        super().tearDown()

    def create_auth_and_check(self, method: str, endpoint: str):
        pass
        # """
        # creates test auth data and validates @auth_required endpoint
        # """
        # from tests.tools import create_test_auth

        # # not authorized
        # logger.debug('> not authorized')
        # res = self.test_client.open(endpoint, method=method)
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 401)
        # self.assertEqual(data['message'], 'Not authorized')

        # # invalid token
        # logger.debug('> invalid token')
        # res = self.test_client.open(endpoint, method=method, headers={'access_token': '1'})
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 401)
        # self.assertEqual(data['message'], 'Invalid token')

        # # token expired
        # logger.debug('> token expired')

        # user, consumer, auth, session = create_test_auth()
        # auth.expire_date = datetime.utcnow() + timedelta(seconds=-10)
        # session.add(auth)
        # session.commit()

        # res = self.test_client.open(endpoint, method=method,
        #                             headers={'access_token': auth.access_token})
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 401)
        # self.assertEqual(data['message'], 'Token expired')

        # # back valid date
        # auth.expire_date = datetime.utcnow() + timedelta(seconds=10000)
        # session.merge(auth)
        # session.commit()

        # return (user, consumer, auth, session)


def create_app():
    """ yeah """
    global app
    app = tornado.web.Application(debug=True)

    # init mongodb
    from app.model import model
    model.init('tornado-test-test')

    # init rest
    from app.rest import rest
    rest.init(app)


def init():
    """
    starts tests
    """
    logging.basicConfig(
        format='%(asctime)s %(levelname).1s[%(module)s:%(lineno)d]:%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.DEBUG)
    logging.debug('initializing test app. pid: %d', os.getpid())


if __name__ == '__main__':
    import sys
    sys.path.append(os.getcwd())

    if len(sys.argv) == 1:
        sys.argv.append('user_api_tests')

    init()
    tornado.testing.main()
