"""
unit tests for auth_api.py
"""
from logging import getLogger
from datetime import datetime, timedelta

from tests.main import UnitTest
from tests.tools import create_test_auth
from tests.tools import auth_headers

from app.orm.models import Auth

from flask import json

logger = getLogger()


class AuthApiTests(UnitTest):
    """
    unit tests for AuthAPI
    """
    def test_get(self):
        """
        GET /auth/<secret>
        """
        logger.debug('***** GET *****')

        # no secret
        logger.debug('> no secret')
        res = self.test_client.get('/auth')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message'], 'No secret')

        # not authorized
        logger.debug('> not authorized')
        res = self.test_client.get('/auth', headers={'secret': '1'})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message'], 'Not authorized')

        auth = create_test_auth()

        # incorrect email
        logger.debug('> incorrect email')
        res = self.test_client.get(
            '/auth',
            headers={**auth_headers('brooth@gmail.co', '123'), **{'secret': '1'}})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message'], 'Invalid credentials')

        # incorrect password
        logger.debug('> incorrect password')
        res = self.test_client.get(
            '/auth',
            headers={**auth_headers('brooth@gmail.co', '12'), **{'secret': '1'}})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message'], 'Invalid credentials')

        # Invalid secret
        logger.debug('> invalid secret')

        res = self.test_client.get(
            '/auth',
            headers={**auth_headers('brooth@gmail.com', '123'), **{'secret': '1'}})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message'], 'Invalid secret')

        # returns same auth
        logger.debug('> returns same auth')

        res = self.test_client.get(
            '/auth',
            headers={**auth_headers('brooth@gmail.com', '123'), **{'secret': auth[1].secret}})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['access_token'], auth[2].access_token)
        self.assertEqual(data['refresh_token'], auth[2].refresh_token)

        # returns new auth
        logger.debug('> returns new auth')
        auth[3].delete(auth[2])
        auth[3].commit()

        res = self.test_client.get(
            '/auth',
            headers={**auth_headers('brooth@gmail.com', '123'), **{'secret': auth[1].secret}})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 200)
        self.assertNotEqual(data['access_token'], auth[2].access_token)
        self.assertNotEqual(data['refresh_token'], auth[2].refresh_token)

    def test_put(self):
        """
        PUT /auth/<refresh_token>
        """
        logger.debug('***** PUT *****')

        # no refresh token
        logger.debug('> no refresh token')
        res = self.test_client.put('/auth')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message'], 'No refresh token')

        # Invalid refresh_token
        logger.debug('> Invalid refresh_token')
        res = self.test_client.put('/auth', headers={'refresh_token': '1'})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message'], 'Invalid refresh token')

        # valid token
        logger.debug('> valid token')
        _, _, auth, session = create_test_auth()

        res = self.test_client.put('/auth', headers={'refresh_token': auth.refresh_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Token is valid. No need to refresh')

        # updates expired token
        logger.debug('> updates expired token')
        auth.expire_date = datetime.utcnow() + timedelta(seconds=-10)
        session.merge(auth)
        session.commit()

        res = self.test_client.put('/auth', headers={'refresh_token': auth.refresh_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 200)

        # expire_date not later that end_date
        logger.debug('> expire_date not later that end_date')

        auth.end_date = datetime.utcnow() + timedelta(seconds=60)
        session.merge(auth)
        session.commit()

        res = self.test_client.put('/auth', headers={'refresh_token': auth.refresh_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 200)
        self.assertLessEqual(int(data['expires_in']), 60)

    def test_delete(self):
        """
        DELETE /auth/<refresh_token>
        """
        logger.debug('***** DELETE *****')

        # no refresh token
        logger.debug('> no refresh token')
        res = self.test_client.delete('/auth')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message'], 'No refresh token')

        # Invalid refresh_token
        logger.debug('> Invalid refresh_token')
        res = self.test_client.delete('/auth', headers={'refresh_token': '1'})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        # deletes token
        logger.debug('> deletes token')
        _, _, auth, session = create_test_auth()

        res = self.test_client.delete('/auth', headers={'refresh_token': auth.refresh_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data, 'OK')
        self.assertIsNone(session.query(Auth).get(auth.id))
