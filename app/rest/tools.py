# pylint: disable=locally-disabled, invalid-name
"""
Tools for REST package
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


def _prepare_doc(doc):
    # pylint: disable=locally-disabled, unidiomatic-typecheck
    """ prepares a doc to jsonify """
    if '_id' in doc:
        doc['id'] = doc.pop('_id')
    for key, value in doc.items():
        if type(value) == ObjectId:
            doc[key] = str(value)
    return doc


def jsonify(doc):
    """ document to json. escapes '_id' """
    doc = _prepare_doc(doc)
    return json.dumps(doc, sort_keys=True)


async def jsonify_list(docs):
    """ list of documents to json. escapes '_id' """
    data = []
    async for doc in docs:
        doc = _prepare_doc(doc)
        data.append(doc)
    return json.dumps(data, sort_keys=True)


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


def _get_auth_code(handler, method):
    from app.rest.rest import ErrorResponse

    creds = handler.request.headers.get('Authorization')
    if not creds:
        raise ErrorResponse('Not authorized', 401)

    if not creds.startswith(method):
        raise ErrorResponse('API requires %s authorization' % method)

    return creds[len(method) + 1:]


def auth_required(function=None, *, barier=True, secret=False):
    """
    decorator check barier auth and passes a "_user_id" through kwargs
    """
    def decorator(fun):
        """ decorator """
        @wraps(fun)
        async def wrapper(self, *args, **kwargs):
            """ wrapper """
            from app.model.model import db
            from app.rest.rest import ErrorResponse

            if barier:
                token = _get_auth_code(self, 'Bearer')
                auth = await db.auths.find_one({'access_token': token},
                                               {'user_id': 1, 'expire_date': 1})
                if not auth:
                    raise ErrorResponse('Invalid token', 401)
                if datetime.utcnow() > auth['expire_date']:
                    raise ErrorResponse('Token expired', 401)
                kwargs['_user_id'] = auth['user_id']

            if secret:
                code = _get_auth_code(self, 'Secret')
                consumer = await db.consumers.find_one({'secret_code': code}, {'_id': 1})
                if not consumer:
                    raise ErrorResponse('Invalid secret code', 401)
                kwargs['_consumer_id'] = consumer['_id']

            await fun(self, *args, **kwargs)
        return wrapper
    return decorator if not function else decorator(function)
