"""
tests for consumer_api.py
"""
import logging

from tests.main import UnitTest
from tests.tools import auth_headers

from app.orm.models import Session, User, Consumer
from app.rest.tools import password_hash, gen_token

from flask import json

logger = logging.getLogger()


class ConsumerApiTests(UnitTest):
    """
    tests for ConsumerAPI
    """
    def test_get_all(self):
        """
        GET /consumer
        """
        logger.debug('test_get_all()')

        # no credentials
        logger.debug('> w/out credentials')
        res = self.test_client.get('/consumer')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message'], 'No credentials')

        session = Session()
        user = User()
        user.gen_id()
        user.email = 'brooth@gmail.com'
        user.password = password_hash('123')
        session.add(user)
        session.commit()

        # incorrect email
        logger.debug('> incorrect email')
        res = self.test_client.get('/consumer', headers=auth_headers('brooth@gmail.co', '123'))
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message'], 'Invalid credentials')

        # incorrect password
        logger.debug('> incorrect password')
        res = self.test_client.get('/consumer', headers=auth_headers('brooth@gmail.com', '12'))
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message'], 'Invalid credentials')

        # no data
        logger.debug('> no data')
        res = self.test_client.get('/consumer', headers=auth_headers('brooth@gmail.com', '123'))
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data), 0)

        # returns new item
        consumer = Consumer()
        consumer.gen_id()
        consumer.name = 'test consumer'
        consumer.secret = gen_token()
        consumer.user_id = user.id
        session.add(consumer)
        session.commit()

        logger.debug('check new item')
        res = self.test_client.get('/consumer', headers=auth_headers('brooth@gmail.com', '123'))
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data), 1)
        item = data[0]
        self.assertEqual(item['id'], consumer.id)
        self.assertEqual(item['name'], 'test consumer')

        # returns two items
        consumer2 = Consumer()
        consumer2.gen_id()
        consumer2.name = 'test consumer2'
        consumer2.secret = gen_token()
        consumer2.user_id = user.id
        session.add(consumer2)
        session.commit()

        logger.debug('check new item')
        res = self.test_client.get('/consumer', headers=auth_headers('brooth@gmail.com', '123'))
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data), 2)
        item = data[0] if data[0]['id'] == consumer2.id else data[1]
        self.assertEqual(item['name'], 'test consumer2')

        # doen't return deleted item
        logger.debug('doen\'t return deleted item')
        session.delete(consumer2)
        session.commit()

        res = self.test_client.get('/consumer', headers=auth_headers('brooth@gmail.com', '123'))
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data), 1)
        item = data[0]
        self.assertEqual(item['id'], consumer.id)
        self.assertEqual(item['name'], 'test consumer')

    def test_get(self):
        """
        GET /consumer/<uuid>
        """
        logger.debug('test_get()')

        # no credentials
        logger.debug('> no credentials')
        res = self.test_client.get('/consumer/1')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message'], 'No credentials')

        session = Session()
        user = User()
        user.gen_id()
        user.email = 'brooth@gmail.com'
        user.password = password_hash('123')
        session.add(user)
        session.commit()
        session.expunge(user)

        # incorrect email
        logger.debug('> incorrect email')
        res = self.test_client.get('/consumer/1', headers=auth_headers('brooth@gmail.co', '123'))
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message'], 'Invalid credentials')

        # incorrect email
        logger.debug('> incorrect password')
        res = self.test_client.get('/consumer/1', headers=auth_headers('brooth@gmail.com', '12'))
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message'], 'Invalid credentials')

        # Invalid UUID
        logger.debug('> invalid uuid')
        res = self.test_client.get('/consumer/1', headers=auth_headers('brooth@gmail.com', '123'))
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Bad UUID')

        # consumer not found
        logger.debug('> consumer not found')

        consumer = Consumer()
        consumer.gen_id()

        res = self.test_client.get('/consumer/' + consumer.id,
                                   headers=auth_headers('brooth@gmail.com', '123'))
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Consumer not found')

        # returns new consumer
        logger.debug('> returns new consumer')

        consumer.name = 'test consumer'
        consumer.secret = gen_token()
        consumer.user_id = user.id
        session.add(consumer)
        session.commit()

        res = self.test_client.get('/consumer/' + consumer.id,
                                   headers=auth_headers('brooth@gmail.com', '123'))
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['secret'], consumer.secret)

        # doesn't return deleted consumer
        logger.debug('> doesn\'t return deleted consumer')

        session.delete(consumer)

        res = self.test_client.get('/consumer/' + consumer.id,
                                   headers=auth_headers('brooth@gmail.com', '123'))
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Consumer not found')

    def test_post(self):
        """
        POST /consumer/<uuid>
        """
        logger.debug('test_post()')

        # method put not supported
        logger.debug('> method post not supported')
        res = self.test_client.post('/consumer')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['message'], 'Method POST not supported')

    def test_put(self):
        """
        PUT /consumer/<uuid>
        """
        logger.debug('test_put()')

        # method put not supported
        logger.debug('> method put not supported')
        res = self.test_client.put('/consumer')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['message'], 'Method PUT not supported')

        # no credentials
        logger.debug('> no credentials')
        res = self.test_client.put('/consumer/1')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message'], 'No credentials')

        session = Session()
        user = User()
        user.gen_id()
        user.email = 'brooth@gmail.com'
        user.password = password_hash('123')
        session.add(user)
        session.commit()
        session.expunge(user)

        # incorrect email
        logger.debug('> incorrect email')
        res = self.test_client.put('/consumer/1', headers=auth_headers('brooth@gmail.co', '123'))
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message'], 'Invalid credentials')

        # incorrect email
        logger.debug('> incorrect password')
        res = self.test_client.put('/consumer/1', headers=auth_headers('brooth@gmail.com', '12'))
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message'], 'Invalid credentials')

        # Invalid UUID
        logger.debug('> invalid uuid')
        res = self.test_client.put('/consumer/1', headers=auth_headers('brooth@gmail.com', '123'))
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Bad UUID')

        # consumer not found
        logger.debug('> consumer not found')

        consumer = Consumer()
        consumer.gen_id()

        res = self.test_client.put('/consumer/' + consumer.id,
                                   headers=auth_headers('brooth@gmail.com', '123'))
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Consumer not found')

        # returns new consumer
        logger.debug('> returns new consumer')

        secret = gen_token()
        logger.debug('secret: ' + secret)
        consumer.name = 'test consumer'
        consumer.secret = secret
        consumer.user_id = user.id
        session.add(consumer)
        session.commit()

        res = self.test_client.put('/consumer/' + consumer.id,
                                   headers=auth_headers('brooth@gmail.com', '123'))
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 200)
        self.assertNotEqual(data['secret'], secret)

        # doesn't return deleted consumer
        logger.debug('> doesn\'t return deleted consumer')

        session.delete(consumer)

        res = self.test_client.put('/consumer/' + consumer.id,
                                   headers=auth_headers('brooth@gmail.com', '123'))
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Consumer not found')

    def test_delete(self):
        """
        DELETE /consumer/<uuid>
        """
        logger.debug('test_delete()')

        # method delete not supported
        logger.debug('> method delete not supported')
        res = self.test_client.delete('/consumer')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['message'], 'Method DELETE not supported')

        # no credentials
        logger.debug('> no credentials')
        res = self.test_client.delete('/consumer/1')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message'], 'No credentials')

        session = Session()
        user = User()
        user.gen_id()
        user.email = 'brooth@gmail.com'
        user.password = password_hash('123')
        session.add(user)
        session.commit()
        session.expunge(user)

        # incorrect email
        logger.debug('> incorrect email')
        res = self.test_client.delete('/consumer/1', headers=auth_headers('brooth@gmail.co', '123'))
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message'], 'Invalid credentials')

        # incorrect email
        logger.debug('> incorrect password')
        res = self.test_client.delete('/consumer/1', headers=auth_headers('brooth@gmail.com', '12'))
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message'], 'Invalid credentials')

        # Invalid UUID
        logger.debug('> invalid uuid')
        res = self.test_client.delete('/consumer/1',
                                      headers=auth_headers('brooth@gmail.com', '123'))
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Bad UUID')

        # consumer not found
        logger.debug('> consumer not found')

        consumer = Consumer()
        consumer.gen_id()

        res = self.test_client.delete('/consumer/' + consumer.id,
                                      headers=auth_headers('brooth@gmail.com', '123'))
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Consumer not found')

        # deletes new consumer
        logger.debug('> deletes new consumer')

        consumer.name = 'test consumer'
        consumer.secret = gen_token()
        consumer.user_id = user.id
        session.add(consumer)
        session.commit()

        res = self.test_client.delete('/consumer/' + consumer.id,
                                      headers=auth_headers('brooth@gmail.com', '123'))
        data = res.get_data(as_text=True)
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 200)
        self.assertNotEqual(data, 'OK')

        self.assertIsNone(session.query(Consumer).get(consumer.id))

        # doesn't delete deleted consumer
        logger.debug('doesn\'t delete deleted consumer')

        res = self.test_client.delete('/consumer/' + consumer.id,
                                      headers=auth_headers('brooth@gmail.com', '123'))
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Consumer not found')
