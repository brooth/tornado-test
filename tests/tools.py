"""
Test package tools
"""
from datetime import datetime, timedelta
import json

from app.rest.tools import password_hash, gen_token
from app.model import model


def read_json(response):
    """ raeds body and jsonifys it """
    if len(response.body) == 0:
        return {}
    return json.loads(response.body.decode('utf8'))

async def create_test_auth():
    """
    creates sample auth, user, consumer
    returns tuple models + session
    """
    user = {
        'email': 'brooth@gmail.com',
        'password': password_hash('123'),
        'name': 'test user'
    }
    user['id'] = await model.db.users.insert(user)

    consumer = await create_consumer(user['id'])
    auth = await create_auth(user['id'], consumer['id'])

    return (user, consumer, auth)


async def create_consumer(user_id):
    """ sample consumer """
    consumer = {
        'secret': gen_token(2),
        'user_id': user_id,
        'name': 'test consumer'
    }
    consumer['id'] = await model.db.consumers.insert(consumer)
    return consumer


async def create_auth(user_id, consumer_id):
    """ sample Auth """
    auth = {
        'access_token': gen_token(),
        'refresh_token': gen_token(2),
        'expire_date': datetime.utcnow() + timedelta(seconds=60),
        'end_date': datetime.utcnow() + timedelta(seconds=60),
        'user_id': user_id,
        'consumer_id': consumer_id
    }
    auth['id'] = await model.db.auths.insert(auth)
    return auth


def auth_headers(username, password):
    """ header with basic http auth credentials """
    import base64

    return {'Authorization': 'Basic %s' % base64.b64encode(
        bytes(username + ':' + password, 'utf-8')).decode('ascii')}


# def create_sample_db():
#     """
#     creates a db with sample data
#     """
#     from sqlalchemy import create_engine
#     import app.orm.models
#     import tests.models

#     app.orm.models.init(create_engine('sqlite:///pb-test.db', convert_unicode=True, echo=True))
#     app.orm.models.Base.metadata.drop_all()
#     app.orm.models.Base.metadata.create_all()
#     tests.models.sample_data()
