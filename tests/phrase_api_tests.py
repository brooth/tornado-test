"""
unit tests for phrase_api.py
"""
import uuid
from logging import getLogger
from tests.main import UnitTest
from app.orm.models import Phrase, Lang, Session, Phrasebook, PhrasebookPhrase
from flask import json

logger = getLogger()


class PhraseApiTests(UnitTest):
    """
    unit tests for PhraseAPI
    """
    def test_get(self):
        """
        GET /phrase/<uuid>
        """
        logger.debug('***** GET *****')

        # Invalid UUID
        logger.debug('> invalid uuid')
        res = self.test_client.get('/phrase/1')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Bad UUID')

        # phrase not found
        logger.debug('> phrase not found')

        res = self.test_client.get('/phrase/' + str(uuid.uuid4()))
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'Phrase not found')

        # returns new phrase
        logger.debug('> returns new phrase')

        session = Session()
        l = Lang()
        l.key = 'en'
        l.code = 'en'
        session.add(l)
        session.flush()

        p = Phrase()
        p.gen_id()
        p.text1 = 't1'
        p.text2 = 't2'
        p.lang1 = 'en'
        p.lang2 = 'en'
        session.add(p)
        session.commit()

        res = self.test_client.get('/phrase/' + str(p.id))
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['text1'], 't1')
        self.assertEqual(data['text2'], 't2')
        self.assertEqual(data['lang1'], 'en')
        self.assertEqual(data['lang2'], 'en')

    def test_post(self):
        """
        POST /phrase/<phrasybook>
        """
        logger.debug('***** POST *****')

        user, _, auth, session = self.create_auth_and_check('POST', '/phrase/1')

        # Invalid UUID
        logger.debug('> invalid uuid')
        res = self.test_client.post('/phrase/1', headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Bad UUID')

        # missing data
        logger.debug('> missing data')

        res = self.test_client.post('/phrase/' + str(user.id),
                                    headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'],
                         "Missing required data ('text1', 'text2', 'lang1', 'lang2')")

        # no empty data
        logger.debug('> no empty data')

        res = self.test_client.post('/phrase/' + str(user.id),
                                    headers={'access_token': auth.access_token},
                                    data=json.dumps({
                                        'text1': '',
                                        'text2': '',
                                        'lang1': '',
                                        'lang2': ''
                                    }),
                                    content_type='application/json')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'],
                         "Missing required data ('text1', 'text2', 'lang1', 'lang2')")

        # too long text
        logger.debug('> too long text')

        res = self.test_client.post('/phrase/' + str(user.id),
                                    headers={'access_token': auth.access_token},
                                    data=json.dumps({
                                        'text1': ('t' * 201),
                                        'text2': 'a',
                                        'lang1': 'a',
                                        'lang2': 'a'
                                    }),
                                    content_type='application/json')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Text must be in range 1..200')

        # phrasebook not found
        logger.debug('> phrasebook not found')

        res = self.test_client.post('/phrase/' + str(user.id),
                                    headers={'access_token': auth.access_token},
                                    data=json.dumps({
                                        'text1': 'a',
                                        'text2': 'a',
                                        'lang1': 'a',
                                        'lang2': 'a'
                                    }),
                                    content_type='application/json')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'Phrasebook not found')

        p = Phrasebook()
        p.gen_id()
        p.name = 'new pb'
        p.user_id = user.id
        session.add(p)

        l = Lang()
        l.key = 'en'
        l.codes = ' eng '
        session.add(l)
        session.commit()

        # uknown lang
        logger.debug('> uknown lang')

        res = self.test_client.post('/phrase/' + str(p.id),
                                    headers={'access_token': auth.access_token},
                                    data=json.dumps({
                                        'text1': 't1',
                                        'text2': 't2',
                                        'lang1': 'a1',
                                        'lang2': 'a2'
                                    }),
                                    content_type='application/json')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], "Unknown lang 'a1'")

        # creates new phrasebook
        logger.debug('> creates new phrasebook')
        res = self.test_client.post('/phrase/' + str(p.id),
                                    headers={'access_token': auth.access_token},
                                    data=json.dumps({
                                        'text1': 't1',
                                        'text2': 't2',
                                        'lang1': 'eng',
                                        'lang2': 'eng'
                                    }),
                                    content_type='application/json')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['text1'], 't1')
        self.assertEqual(data['text2'], 't2')
        self.assertEqual(data['lang1'], 'en')
        self.assertEqual(data['lang2'], 'en')
        self.assertIsNotNone(session.query(PhrasebookPhrase).filter(
            PhrasebookPhrase.phrasebook_id == p.id,
            PhrasebookPhrase.phrase_id == data['id']).first())

    def test_copy(self):
        """
        POST /phrase/<phrasebook>/<phrase>
        """
        logger.debug('***** COPY *****')

        user, _, auth, session = self.create_auth_and_check('POST', '/phrase/1/2')

        # Invalid phrasebook UUID
        logger.debug('> invalid phrasebook uuid')
        res = self.test_client.post('/phrase/1/2', headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Bad UUID')

        # Invalid phrase UUID
        logger.debug('> invalid phrase uuid')
        res = self.test_client.post('/phrase/%s/2' % str(user.id),
                                    headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Bad UUID')

        # phrasebook not found
        logger.debug('> phrasebook not found')

        res = self.test_client.post('/phrase/%s/%s' % (str(user.id), str(user.id)),
                                    headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'Phrasebook not found')

        p = Phrasebook()
        p.gen_id()
        p.name = 'new pb'
        p.user_id = user.id
        session.add(p)

        l = Lang()
        l.key = 'en'
        l.codes = ' eng '
        session.add(l)
        session.flush()

        ph = Phrase()
        ph.gen_id()
        ph.text1 = 't1'
        ph.text2 = 't2'
        ph.lang1 = 'en'
        ph.lang2 = 'en'
        session.add(ph)
        session.commit()

        # phrase not found
        logger.debug('> phrase not found')

        res = self.test_client.post('/phrase/%s/%s' % (str(p.id), str(user.id)),
                                    headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'Phrase not found')

        # copies phrase
        logger.debug('> copies phrase')

        res = self.test_client.post('/phrase/%s/%s' % (str(p.id), str(ph.id)),
                                    headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data, 'OK')
        self.assertIsNotNone(session.query(PhrasebookPhrase).filter(
            PhrasebookPhrase.phrasebook_id == p.id,
            PhrasebookPhrase.phrase_id == ph.id).first())

        # phrase already exists
        logger.debug('> phrase already exists')

        res = self.test_client.post('/phrase/%s/%s' % (str(p.id), str(ph.id)),
                                    headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Phrase already exists')

    def test_put(self):
        """
        PUT /phrase/<phrasybook_uuid>/<phrase_uuid>
        """
        logger.debug('***** PUT *****')

        user, _, auth, session = self.create_auth_and_check('PUT', '/phrase/1/2')

        # Invalid phrasebook UUID
        logger.debug('> invalid phrasebook uuid')
        res = self.test_client.put('/phrase/1/2', headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Bad UUID')

        # Invalid phrase UUID
        logger.debug('> invalid phrase uuid')
        res = self.test_client.put('/phrase/%s/2' % str(user.id),
                                   headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Bad UUID')

        # updating langs not allowed
        logger.debug('> updating langs not allowed')

        res = self.test_client.put('/phrase/%s/%s' % (str(user.id), str(user.id)),
                                   headers={'access_token': auth.access_token},
                                   content_type='application/json',
                                   data=json.dumps({
                                       'lang1': 'a',
                                       'lang2': 'a'
                                   }))
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Updating langs not allowed')

        # nothing to update
        logger.debug('> nothing to update')

        res = self.test_client.put('/phrase/%s/%s' % (str(user.id), str(user.id)),
                                   headers={'access_token': auth.access_token},
                                   content_type='application/json',
                                   data=json.dumps({
                                       'mis': 'a'
                                   }))
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Nothing to update')

        # no empty text
        logger.debug('> no empty text')

        res = self.test_client.put('/phrase/%s/%s' % (str(user.id), str(user.id)),
                                   headers={'access_token': auth.access_token},
                                   data=json.dumps({
                                       'text1': '',
                                       'text2': 't2',
                                   }),
                                   content_type='application/json')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Text must be in range 1..200')

        # too long text
        logger.debug('> too long text')

        res = self.test_client.put('/phrase/%s/%s' % (str(user.id), str(user.id)),
                                   headers={'access_token': auth.access_token},
                                   data=json.dumps({
                                       'text2': ('t' * 201)
                                   }),
                                   content_type='application/json')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Text must be in range 1..200')

        # phrasebook not found
        logger.debug('> phrasebook not found')

        res = self.test_client.put('/phrase/%s/%s' % (str(user.id), str(user.id)),
                                   headers={'access_token': auth.access_token},
                                   data=json.dumps({
                                       'text2': 't2'
                                   }),
                                   content_type='application/json')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'Phrasebook not found')

        p = Phrasebook()
        p.gen_id()
        p.name = 'new pb'
        p.user_id = user.id
        session.add(p)

        l = Lang()
        l.key = 'en'
        l.codes = ' eng '
        session.add(l)
        session.flush()

        ph = Phrase()
        ph.gen_id()
        ph.text1 = 't1'
        ph.text2 = 't2'
        ph.lang1 = 'en'
        ph.lang2 = 'en'
        session.add(ph)
        session.flush()

        pp = PhrasebookPhrase()
        pp.gen_id()
        pp.phrasebook_id = p.id
        pp.phrase_id = ph.id
        session.add(pp)
        session.commit()

        # phrase not found
        logger.debug('> phrase not found')

        res = self.test_client.put('/phrase/%s/%s' % (str(p.id), str(user.id)),
                                   headers={'access_token': auth.access_token},
                                   data=json.dumps({
                                       'text2': 't2'
                                   }),
                                   content_type='application/json')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'Phrase not found')

        # updates phrase
        logger.debug('> updates phrase')

        res = self.test_client.put('/phrase/%s/%s' % (str(p.id), str(ph.id)),
                                   headers={'access_token': auth.access_token},
                                   data=json.dumps({
                                       'text2': 't2.2'
                                   }),
                                   content_type='application/json')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['id'], ph.id)
        self.assertEqual(session.query(Phrase).get(ph.id).text2, 't2.2')

        # creates a copy if many phrasebooks
        logger.debug('> creates a copy if many phrasebooks')

        p2 = Phrasebook()
        p2.gen_id()
        p2.name = 'new pb2'
        p2.user_id = user.id
        session.add(p2)
        session.flush()

        pp = PhrasebookPhrase()
        pp.gen_id()
        pp.phrasebook_id = p2.id
        pp.phrase_id = ph.id
        session.add(pp)
        session.commit()

        res = self.test_client.put('/phrase/%s/%s' % (str(p.id), str(ph.id)),
                                   headers={'access_token': auth.access_token},
                                   data=json.dumps({
                                       'text2': 't2.3'
                                   }),
                                   content_type='application/json')
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 200)
        self.assertNotEqual(data['id'], ph.id)
        self.assertEqual(session.query(Phrase).get(ph.id).text2, 't2.2')
        self.assertEqual(session.query(Phrase).get(data['id']).text2, 't2.3')

    def test_delete(self):
        """
        DELETE /phrase/<phrasybook_uuid>/<phrase_uuid>
        """
        logger.debug('***** DELETE *****')

        user, _, auth, session = self.create_auth_and_check('DELETE', '/phrase/1/2')

        # Invalid phrasebook UUID
        logger.debug('> invalid phrasebook uuid')
        res = self.test_client.delete('/phrase/1/2', headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Bad UUID')

        # Invalid phrase UUID
        logger.debug('> invalid phrase uuid')
        res = self.test_client.delete('/phrase/%s/2' % str(user.id),
                                   headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Bad UUID')

        # phrasebook not found
        logger.debug('> phrasebook not found')

        res = self.test_client.delete('/phrase/%s/%s' % (str(user.id), str(user.id)),
                                    headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'Phrasebook not found')

        p = Phrasebook()
        p.gen_id()
        p.name = 'new pb'
        p.user_id = user.id
        session.add(p)

        p2 = Phrasebook()
        p2.gen_id()
        p2.name = 'new pb2'
        p2.user_id = user.id
        session.add(p2)

        l = Lang()
        l.key = 'en'
        l.codes = ' eng '
        session.add(l)
        session.flush()

        ph = Phrase()
        ph.gen_id()
        ph.text1 = 't1'
        ph.text2 = 't2'
        ph.lang1 = 'en'
        ph.lang2 = 'en'
        session.add(ph)
        session.flush()

        pp = PhrasebookPhrase()
        pp.gen_id()
        pp.phrasebook_id = p.id
        pp.phrase_id = ph.id
        session.add(pp)

        pp2 = PhrasebookPhrase()
        pp2.gen_id()
        pp2.phrasebook_id = p2.id
        pp2.phrase_id = ph.id
        session.add(pp2)
        session.commit()

        # phrase not found
        logger.debug('> phrase not found')

        res = self.test_client.delete('/phrase/%s/%s' % (str(p.id), str(user.id)),
                                    headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'Phrase not found')

        # deletes only pp if many phrasebooks
        logger.debug('> deletes only pp if many phrasebooks')

        res = self.test_client.delete('/phrase/%s/%s' % (str(p.id), str(ph.id)),
                                    headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data, 'OK')
        self.assertIsNotNone(session.query(Phrase).get(ph.id))
        self.assertIsNone(session.query(PhrasebookPhrase).get(pp.id))
        self.assertIsNotNone(session.query(PhrasebookPhrase).get(pp2.id))

        # deletes phrase
        logger.debug('> deletes phrase')

        res = self.test_client.delete('/phrase/%s/%s' % (str(p2.id), str(ph.id)),
                                    headers={'access_token': auth.access_token})
        data = json.loads(res.get_data(as_text=True))
        logger.debug('< ' + str(data))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data, 'OK')
        self.assertIsNone(session.query(Phrase).get(ph.id))
        self.assertIsNone(session.query(PhrasebookPhrase).get(pp2.id))
