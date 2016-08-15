"""
Token Authorization APIs
"""

from datetime import datetime, timedelta
from bson.objectid import ObjectId

from app.model.model import db
from app.rest.rest import Handler
from app.rest.tools import auth_required, jsonify, password_hash, gen_token

# TODO: scheduler (new process) deletes ended tokens
TOKEN_ENDS_IN_SECONDS = 7776000   # 3 months
TOKEN_EXPIRES_IN_SECONDS = 86400  # 1 day


class AuthAPI(Handler):
    # pylint: disable=locally-disabled, abstract-method
    """
    APIs /auth
    """
    @auth_required(secret=True, barier=False)
    async def get(self, user_id, _consumer_id=None):
        # pylint: disable=locally-disabled, arguments-differ
        """
        GET /auth
        """
        user_id = ObjectId(user_id)

        auth = await db.auths.find_one({'consumer_id': _consumer_id, 'user_id': user_id})
        if not auth:
            auth = {}
            auth['user_id'] = user_id
            auth['consumer_id'] = _consumer_id
            auth['access_token'] = gen_token()
            auth['refresh_token'] = gen_token(2)
            auth['expire_date'] = datetime.utcnow() + timedelta(seconds=TOKEN_EXPIRES_IN_SECONDS)
            auth['end_date'] = datetime.utcnow() + timedelta(seconds=TOKEN_ENDS_IN_SECONDS)
            await db.auths.insert(auth)

        expires_in = int((auth['expire_date'] - datetime.utcnow()).total_seconds())

        self.write(jsonify({
            'access_token': auth['access_token'],
            'refresh_token': auth['refresh_token'],
            'expires_in': expires_in
        }))

    # # TODO: update 'expires_in'?
    # # TODO: add basic authorization

    # @staticmethod
    # @call_in_transaction
    # def put(_session=None):
    #     """
    #     PUT /auth
    #     """
    #     refresh_token = request.headers.get('refresh_token')
    #     if not refresh_token:
    #         return access_denied('No refresh token')

    #     auth = _session.query(Auth).filter(Auth.refresh_token == refresh_token).first()
    #     if not auth:
    #         return access_denied('Invalid refresh token')
    #     if datetime.utcnow() < auth.expire_date:
    #         return bad_request('Token is valid. No need to refresh')

    #     auth.access_token = gen_token()
    #     auth.expire_date = datetime.utcnow() + timedelta(seconds=TOKEN_EXPIRES_IN_SECONDS)
    #     if auth.expire_date > auth.end_date:
    #         auth.expire_date = auth.end_date
    #     auth.expires_in = int((auth.expire_date - datetime.utcnow()).total_seconds())

    #     return jsonify({
    #         'access_token': auth.access_token,
    #         'expires_in': auth.expires_in
    #     })

    # # TODO: add basic authorization
    # @staticmethod
    # @call_in_transaction
    # def delete(_session=None):
    #     """ DELETE /auth -H 'refresh_token' """
    #     refresh_token = request.headers.get('refresh_token')
    #     if not refresh_token:
    #         return access_denied('No refresh token')

    #     if _session.query(Auth).filter(Auth.refresh_token == refresh_token).delete() == 0:
    #         return access_denied('Invalid refresh token')
    #     return jsonify('OK')
