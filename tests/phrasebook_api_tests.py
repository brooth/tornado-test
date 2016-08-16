"""
unit tests for phrasebook_api.py
"""
from logging import getLogger

from tests.main import UnitTest

from app.orm.models import Phrasebook, User

from flask import json

logger = getLogger()


class PhrasebookApiTests(UnitTest):
    """
    unit tests for PhrasebookAPI
    """
    def test_get_all(self):
        """
        GET /phrasebook
        """
        logger.debug('***** GET ALL *****')

        user, _, auth, session = self.create_auth_and_check('GET', '/phrasebook')

        # no data
        logger.debug('> no data')

        res = self.test_client.get('/phrasebook', headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data), 0)

        # returns new phrasebook
        logger.debug('> returns new phrasebook')

        p = Phrasebook()
        p.gen_id()
        p.name = 'new p'
        p.user_id = user.id
        session.add(p)
        session.commit()

        res = self.test_client.get('/phrasebook', headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'new p')

        # doesn't return removed phraseboook
        logger.debug('> doesn\'t return removed phraseboook')

        session.delete(p)
        session.commit()

        res = self.test_client.get('/phrasebook', headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data), 0)

    def test_get(self):
        """
        GET /phrasebook/<uuid>
        """
        logger.debug('***** GET *****')

        user, _, auth, session = self.create_auth_and_check('GET', '/phrasebook/1')

        # Invalid UUID
        logger.debug('> invalid uuid')
        res = self.test_client.get('/phrasebook/1', headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Bad UUID')

        # phrasebook not found
        logger.debug('> phrasebook not found')

        res = self.test_client.get('/phrasebook/' + str(user.id),
                                   headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'Phrasebook not found')

        # doesn return others phrasebook
        logger.debug('> doesn return others phrasebook')

        user2 = User()
        user2.gen_id()
        user2.email = 'u2'
        user2.password = 'u2'
        user2.name = 'u2'
        session.add(user2)
        session.flush()

        p = Phrasebook()
        p.gen_id()
        p.name = 'new p'
        p.user_id = user2.id
        session.add(p)
        session.commit()

        res = self.test_client.get('/phrasebook/' + str(p.id),
                                   headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'Phrasebook not found')

        # returns new phrasebook
        logger.debug('> returns new phrasebook')

        p.user_id = user.id
        session.merge(p)
        session.commit()

        res = self.test_client.get('/phrasebook/' + str(p.id),
                                   headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['name'], 'new p')

    def test_post(self):
        """
        POST /phrasebook
        """
        logger.debug('***** POST *****')

        _, _, auth, _ = self.create_auth_and_check('POST', '/phrasebook')

        # no data
        logger.debug('> no data')

        res = self.test_client.post('/phrasebook', headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'No data')

        # no empty names
        logger.debug('> no empty names')

        res = self.test_client.post('/phrasebook',
                                    headers={'access_token': auth.access_token},
                                    data=json.dumps({'name': ''}),
                                    content_type='application/json')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Name must be in range 1..100')

        # too long name
        logger.debug('> too long name')

        res = self.test_client.post('/phrasebook',
                                    headers={'access_token': auth.access_token},
                                    data=json.dumps({'name': ('N' * 101)}),
                                    content_type='application/json')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Name must be in range 1..100')

        # returns new phrasebook
        logger.debug('> returns new phrasebook')

        res = self.test_client.post('/phrasebook',
                                    headers={'access_token': auth.access_token},
                                    data=json.dumps({'name': 'phrasybook 1'}),
                                    content_type='application/json')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(data['id'])
        self.assertEqual(data['name'], 'phrasybook 1')

    def test_put(self):
        """
        PUT /phrasebook/<uuid>
        """
        logger.debug('***** PUT *****')

        user, _, auth, session = self.create_auth_and_check('PUT', '/phrasebook/1')

        # Invalid UUID
        logger.debug('> invalid uuid')
        res = self.test_client.put('/phrasebook/1', headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Bad UUID')

        # no data
        logger.debug('> no data')

        res = self.test_client.put('/phrasebook/' + str(user.id),
                                   headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'No data')

        # no empty names
        logger.debug('> no empty names')

        res = self.test_client.put('/phrasebook/' + str(user.id),
                                   headers={'access_token': auth.access_token},
                                   data=json.dumps({'name': ''}),
                                   content_type='application/json')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Name must be in range 1..100')

        # too long name
        logger.debug('> too long name')

        res = self.test_client.put('/phrasebook/' + str(user.id),
                                   headers={'access_token': auth.access_token},
                                   data=json.dumps({'name': ('N' * 101)}),
                                   content_type='application/json')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Name must be in range 1..100')

        # phrasebook not found
        logger.debug('> phrasebook not found')

        res = self.test_client.put('/phrasebook/' + str(user.id),
                                   headers={'access_token': auth.access_token},
                                   data=json.dumps({'name': 'n1'}),
                                   content_type='application/json')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'Phrasebook not found')

        # doesn allow others phrasebook
        logger.debug('> doesn allow others phrasebook')

        user2 = User()
        user2.gen_id()
        user2.email = 'u2'
        user2.password = 'u2'
        user2.name = 'u2'
        session.add(user2)
        session.flush()

        p = Phrasebook()
        p.gen_id()
        p.name = 'new p'
        p.user_id = user2.id
        session.add(p)
        session.commit()

        res = self.test_client.put('/phrasebook/' + str(p.id),
                                   headers={'access_token': auth.access_token},
                                   data=json.dumps({'name': 'n1'}),
                                   content_type='application/json')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'Phrasebook not found')

        # updates new phrasebook
        logger.debug('> updates new phrasebook')

        p.user_id = user.id
        session.merge(p)
        session.commit()

        res = self.test_client.put('/phrasebook/' + str(p.id),
                                   headers={'access_token': auth.access_token},
                                   data=json.dumps({'name': 'n1'}),
                                   content_type='application/json')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data, 'OK')

    def test_delete(self):
        """
        DELETE /phrasebook/<uuid>
        """
        logger.debug('***** DELETE *****')

        user, _, auth, session = self.create_auth_and_check('DELETE', '/phrasebook/1')

        # Invalid UUID
        logger.debug('> invalid uuid')
        res = self.test_client.delete('/phrasebook/1', headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Bad UUID')

        # phrasebook not found
        logger.debug('> phrasebook not found')

        res = self.test_client.delete('/phrasebook/' + str(user.id),
                                      headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'Phrasebook not found')

        # doesn delete others phrasebook
        logger.debug('> doesn delete others phrasebook')

        user2 = User()
        user2.gen_id()
        user2.email = 'u2'
        user2.password = 'u2'
        user2.name = 'u2'
        session.add(user2)
        session.flush()

        p = Phrasebook()
        p.gen_id()
        p.name = 'new p'
        p.user_id = user2.id
        session.add(p)
        session.commit()

        res = self.test_client.delete('/phrasebook/' + str(p.id),
                                      headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'Phrasebook not found')

        # delete new phrasebook
        logger.debug('> delete new phrasebook')

        p.user_id = user.id
        session.merge(p)
        session.commit()

        res = self.test_client.delete('/phrasebook/' + str(p.id),
                                      headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data, 'OK')
