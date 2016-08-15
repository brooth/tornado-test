"""
tools for rest package
"""

import json

from hashlib import sha224
from datetime import datetime
from functools import wraps
from uuid import uuid4
from base64 import b64encode
from logging import getLogger

from bson.objectid import ObjectId

logger = getLogger()


def jsonify(doc):
    """ document to json. escapes '_id' """
    logger.error(type(doc))
    for key, value in doc.items():
        if key == '_id':
            key['id'] = doc.pop(key)
        if type(value) == ObjectId:
            doc[key] = str(value)

    return json.dumps(doc, indent=4, sort_keys=True) + '\n'


async def jsonify_list(docs):
    """ list of documents to json. escapes '_id' """
    data = []
    async for doc in docs:
        for key, value in doc.items():
            if key == '_id':
                key['id'] = doc.pop(key)
            if isinstance(value, ObjectId):
                doc[key] = str(value)
        data.append(doc)
    return json.dumps(data, indent=4, sort_keys=True) + '\n'


def password_hash(password):
    """
    returns sha224 of given password
    """
    return sha224(password.encode('utf-8')).hexdigest()


def gen_token(complexity=1):
    """
    generates a token by random UUIDs
    """
    token = ''
    for _ in range(0, complexity):
        token += b64encode(bytes(str(uuid4()), 'utf8')).decode('utf8')
    return token


def token_auth(function=None):
    """
    decorator check barier auth and passes a "_user_id" through kwargs
    """
    def decorator(fun):
        """ decorator """
        @wraps(fun)
        async def wrapper(self, *args, **kwargs):
            """ wrapper """
            from app.rest.rest import ErrorResponse
            from app.model.model import db

            creds = self.request.headers.get('Authorization')
            if not creds:
                raise ErrorResponse('Not authorized', 401)

            if not creds.startswith('Bearer '):
                raise ErrorResponse('API requires bearer authorization')

            token = creds[len('Bearer '):]
            if not token:
                raise ErrorResponse('Token is empty')

            auth = await db.auths.find_one({'access_token': token})
            if not auth:
                raise ErrorResponse('Invalid token', 401)
            if datetime.utcnow() > auth['expire_date']:
                raise ErrorResponse('Token expired', 401)

            kwargs['_user_id'] = auth['user_id']
            await fun(self, *args, **kwargs)
        return wrapper
    return decorator if not function else decorator(function)
