# pylint: disable=locally-disabled, invalid-name
"""
tests for user_id.py
"""
from logging import getLogger

from tornado.testing import gen_test

from tests.main import UnitTest
from tests.tools import read_json, create_test_auth

logger = getLogger()


class UserApiTests(UnitTest):
    """
    Tests for UserAPI
    """
    @gen_test
    async def test_get(self):
        """
        GET /user
        """
        logger.debug('test_get()')

        # not authorized
        logger.debug('> not authorized')
        res = await self.fetch('/users')
        logger.debug('< ' + str(res.body))
        data = read_json(res)

        self.assertEqual(res.code, 401)
        self.assertEqual(data['message'], 'Not authorized')

        # returns new user
        logger.debug('> returns new user')

        # TODO: create_auth_and_check
        _, _, auth = await create_test_auth()

        res = await self.fetch('/users', headers={
            'Authorization': 'Bearer ' + auth['access_token']
        })
        logger.debug('< ' + str(res.body))
        data = read_json(res)

        self.assertEqual(res.code, 200)
        self.assertEqual(data['name'], 'test user')

    # def test_post(self):
        # """
        # POST /user
        # """
        # logger.debug('test_post()')

        # # empty credentials
        # logger.debug('> empty credentials')

        # res = self.test_client.post('/user')
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 400)
        # self.assertEqual(data['message'], 'Missing required data (email)')

        # # validates email
        # email = 'brooth@gmail.'
        # logger.debug('> validates email %s', email)

        # res = self.test_client.post('/user',
        #                             data=json.dumps({'email': email}),
        #                             content_type='application/json')
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 400)
        # self.assertEqual(data['message'], 'Invalid email %s' % email)

        # email = '@gmail.com'
        # logger.debug('> validates email %s', email)

        # res = self.test_client.post('/user',
        #                             data=json.dumps({'email': email}),
        #                             content_type='application/json')
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 400)
        # self.assertEqual(data['message'], 'Invalid email %s' % email)

        # email = 'brooth.gmail.com'
        # logger.debug('> validates email %s', email)

        # res = self.test_client.post('/user',
        #                             data=json.dumps({'email': email}),
        #                             content_type='application/json')
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 400)
        # self.assertEqual(data['message'], 'Invalid email %s' % email)

        # email = 'brooth.gmail@com'
        # logger.debug('> validates email %s', email)

        # res = self.test_client.post('/user',
        #                             data=json.dumps({'email': email}),
        #                             content_type='application/json')
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 400)
        # self.assertEqual(data['message'], 'Invalid email %s' % email)

        # # too long email
        # email = 'br' + ('o' * 120) + 'th@gmail.com'
        # logger.debug('> too long email %s', email)

        # res = self.test_client.post('/user',
        #                             data=json.dumps({'email': email}),
        #                             content_type='application/json')
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 400)
        # self.assertEqual(data['message'], 'Too long email')

        # # too long password
        # password = ('p' * 21)
        # logger.debug('> too long password %s', password)

        # res = self.test_client.post(
        #     '/user',
        #     data=json.dumps({'email': 'b@gmail.co', 'password': password}),
        #     content_type='application/json')
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 400)
        # self.assertEqual(data['message'], 'Too long password')

        # # too long name
        # name = ('n' * 121)
        # logger.debug('> too long name %s', name)

        # res = self.test_client.post('/user',
        #                             data=json.dumps({'email': 'brooth@gmail.com', 'name': name}),
        #                             content_type='application/json')
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 400)
        # self.assertEqual(data['message'], 'Too long name')

        # # allows empty password
        # logger.debug('> allows empty password')

        # res = self.test_client.post('/user',
        #                             data=json.dumps({
        #                                 'email': 'brooth@gmail.com',
        #                                 'name': 'test usr'
        #                             }),
        #                             content_type='application/json')
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 200)
        # self.assertEqual(data, 'OK')

        # session = Session()
        # user = session.query(User).filter(User.email == 'brooth@gmail.com').first()
        # self.assertIsNotNone(user)

        # # returns new user
        # logger.debug('GET returns new user')
        # consumer = create_consumer(user)
        # session.add(consumer)
        # session.flush()
        # auth = create_auth(user, consumer)
        # session.add(auth)
        # session.commit()

        # res = self.test_client.get('/user', headers={'access_token': auth.access_token})
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 200)
        # self.assertEqual(data['name'], 'test usr')

        # # doesn't allow not unique email
        # logger.debug('> doesn\'t allow not unique email')

        # res = self.test_client.post('/user',
        #                             data=json.dumps({'email': 'brooth@gmail.com'}),
        #                             content_type='application/json')
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 400)
        # self.assertEqual(data['message'], 'Email brooth@gmail.com already exists')

    # def test_put(self):
        # """
        # PUT /user
        # """
        # logger.debug('=== test_put() ===')

        # # not authorized
        # logger.debug('> not authorized')
        # res = self.test_client.put('/user')
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 401)
        # self.assertEqual(data['message'], 'Not authorized')

        # # nothing to put
        # logger.debug('> nothing to put')

        # auth = create_test_auth()
        # session = auth[3]

        # res = self.test_client.put('/user', headers={'access_token': auth[2].access_token})
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 400)
        # self.assertEqual(data['message'], 'Nothing to update')

        # # can't clear email
        # logger.debug('> can\'t clear email')

        # res = self.test_client.put('/user',
        #                            headers={'access_token': auth[2].access_token},
        #                            data=json.dumps({'email': ''}),
        #                            content_type='application/json')
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 400)
        # self.assertEqual(data['message'], 'Invalid email ')

        # # name is too long
        # name = ('N' * 121)
        # logger.debug('> too long name %s', name)

        # res = self.test_client.put('/user',
        #                            headers={'access_token': auth[2].access_token},
        #                            data=json.dumps({'name': name}),
        #                            content_type='application/json')
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 400)
        # self.assertEqual(data['message'], 'Too long name')

        # # too long password
        # password = 'P' * 21
        # logger.debug('> too long password %s', password)

        # res = self.test_client.put('/user',
        #                            headers={'access_token': auth[2].access_token},
        #                            data=json.dumps({'password': password}),
        #                            content_type='application/json')
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 400)
        # self.assertEqual(data['message'], 'Too long password')

        # # no old password
        # logger.debug('> no old password')

        # res = self.test_client.put('/user',
        #                            headers={'access_token': auth[2].access_token},
        #                            data=json.dumps({'password': '123'}),
        #                            content_type='application/json')
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 400)
        # self.assertEqual(data['message'], 'Missing required data(old_password)')

        # # incorrect old password
        # logger.debug('> invalid old password')

        # res = self.test_client.put('/user',
        #                            headers={'access_token': auth[2].access_token},
        #                            data=json.dumps({'password': '123', 'old_password': '1'}),
        #                            content_type='application/json')
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 401)
        # self.assertEqual(data['message'], 'Invalid old password')

        # # changes password. deletes tokens
        # logger.debug('> changes password')

        # res = self.test_client.put('/user',
        #                            headers={'access_token': auth[2].access_token},
        #                            data=json.dumps({'password': '111', 'old_password': '123'}),
        #                            content_type='application/json')
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 200)
        # self.assertEqual(data, 'OK')
        # self.assertEqual(session.query(User).get(
        #     auth[0].id).password, password_hash('111'))
        # self.assertIsNone(session.query(Auth).filter(
        #     Auth.user_id == auth[0].id).first())

        # # restore token
        # session.merge(auth[2])
        # session.commit()

        # # allows clear password
        # logger.debug('> allows clear password')

        # res = self.test_client.put('/user',
        #                            headers={'access_token': auth[2].access_token},
        #                            data=json.dumps({'password': '', 'old_password': '111'}),
        #                            content_type='application/json')
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 200)
        # self.assertEqual(data, 'OK')
        # self.assertEqual(session.query(User).get(auth[0].id).password, password_hash(''))

        # # restore token
        # session.merge(auth[2])
        # session.commit()

        # # changes email
        # logger.debug('> changes email')

        # res = self.test_client.put('/user',
        #                            headers={'access_token': auth[2].access_token},
        #                            data=json.dumps({'email': 'brooth@mail.ru'}),
        #                            content_type='application/json')
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 200)
        # self.assertEqual(data, 'OK')
        # self.assertEqual(session.query(User).get(auth[0].id).email, 'brooth@mail.ru')

        # # changes name
        # logger.debug('> changes name')

        # res = self.test_client.put('/user',
        #                            headers={'access_token': auth[2].access_token},
        #                            data=json.dumps({'name': 'test put user'}),
        #                            content_type='application/json')
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 200)
        # self.assertEqual(data, 'OK')
        # self.assertEqual(session.query(User).get(auth[0].id).name, 'test put user')

        # # changes all
        # logger.debug('> changes all')

        # data = {
        #     'email': 'usr1@mail.ru',
        #     'name': 'name1',
        #     'password': 'pwd1',
        #     'old_password': ''
        # }

        # res = self.test_client.put('/user',
        #                            headers={'access_token': auth[2].access_token},
        #                            data=json.dumps(data),
        #                            content_type='application/json')
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 200)
        # self.assertEqual(data, 'OK')
        # user = session.query(User).get(auth[0].id)
        # self.assertEqual(user.email, 'usr1@mail.ru')
        # self.assertEqual(user.name, 'name1')
        # self.assertEqual(user.password, password_hash('pwd1'))

    # def test_delete(self):
        # """
        # DELETE /user
        # """
        # logger.debug('test_delete()')

        # # not authorized
        # logger.debug('> not authorized')
        # res = self.test_client.delete('/user')
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 401)
        # self.assertEqual(data['message'], 'Not authorized')

        # # deletes user
        # logger.debug('> deletes user')

        # auth = create_test_auth()
        # session = auth[3]

        # res = self.test_client.delete('/user', headers={'access_token': auth[2].access_token})
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 200)
        # self.assertEqual(data, 'OK')
        # self.assertIsNone(session.query(User).get(auth[0].id))

    # def test_check_email(self):
        # """
        # GET /user-tools/check-email-exists/<email>
        # """

        # logger.debug('test_check_email()')

        # # check not exists
        # logger.debug('> check not exists')

        # res = self.test_client.get('/user-tools/check-email-exists/brooth@gmail.com')
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 200)
        # self.assertEqual(data, 'false')

        # # check exists
        # logger.debug('> check exists')

        # session = Session()
        # user = User()
        # user.gen_id()
        # user.email = 'brooth@gmail.com'
        # user.password = '123'
        # session.add(user)
        # session.commit()

        # res = self.test_client.get('/user-tools/check-email-exists/brooth@gmail.com')
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 200)
        # self.assertEqual(data, 'true')

        # # not exists again
        # logger.debug('not exists again')

        # session.delete(user)
        # session.commit()

        # res = self.test_client.get('/user-tools/check-email-exists/brooth@gmail.com')
        # data = json.loads(res.get_data(as_text=True))
        # logger.debug('< ' + str(data))

        # self.assertEqual(res.status_code, 200)
        # self.assertEqual(data, 'false')
