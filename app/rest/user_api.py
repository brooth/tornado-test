"""
User APIs
"""
import re

from app.model.model import db
from app.rest.rest import Handler
from app.rest.tools import auth_required, jsonify, password_hash


class UserAPI(Handler):
    # pylint: disable=locally-disabled, abstract-method
    """
    Manages "/users"
    """
    @auth_required
    async def get(self, _user_id=None):
        # pylint: disable=locally-disabled, arguments-differ
        """
        GET /users
        """
        user = await db.users.find_one({'_id': _user_id}, {'_id': 0, 'name': 1})
        if not user:
            return self.error_response('User not found', 404)
        self.write(jsonify(user))
        self.finish()

    async def post(self):
        """
        POST /users
        """
        data = self.read_json()
        if not data or 'email' not in data:
            return self.error_response('Missing required data (email)')

        email = data['email']
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return self.error_response('Invalid email %s' % email)
        if len(email) > 120:
            return self.error_response('Too long email')
        if await db.users.find_one({'email': email}, {'_id': 1}):
            return self.error_response('Email %s already exists' % email, 400, 100)

        password = data.get('password', '')
        if len(password) > 20:
            return self.error_response('Too long password')

        name = data.get('name')
        if name and len(name) > 120:
            return self.error_response('Too long name')

        user_id = await db.users.insert({
            'email': email,
            'name': name,
            'password': password_hash(password)
        })
        self.write(jsonify({'id': user_id}))

    # @staticmethod
    # @auth_required
    # def put(_user_id=None):
    #     """
    #     PUT /user
    #     """
    #     data = request.get_json(silent=True)
    #     if not data or not any(k in data for k in ('email', 'name', 'password')):
    #         return self.error_response('Nothing to update')

    #     session = Session()
    #     try:
    #         user = session.query(User).get(_user_id)
    #         session.expunge(user)

    #         email = data.get('email')
    #         if email is not None:
    #             if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
    #                 return self.error_response('Invalid email %s' % email)
    #             if len(email) > 120:
    #                 return self.error_response('Too long email')
    #             user.email = email

    #         name = data.get('name')
    #         if name is not None:
    #             if len(name) > 120:
    #                 return self.error_response('Too long name')
    #             user.name = name

    #         password = data.get('password')
    #         if password is not None:
    #             if len(password) > 20:
    #                 return self.error_response('Too long password')
    #             old_password = data.get('old_password')
    #             if old_password is None:
    #                 return self.error_response('Missing required data(old_password)')
    #             if user.password != password_hash(old_password):
    #                 return access_denied('Invalid old password')
    #             user.password = password_hash(password)

    #             # delete all tokens
    #             session.query(Auth).filter(Auth.user_id == _user_id).delete()

    #         session.add(user)
    #         session.commit()
    #     finally:
    #         session.close()

    #     return jsonify('OK')

    # @staticmethod
    # @auth_required
    # @call_in_transaction
    # def delete(_session=None, _user_id=None):
    #     """
    #     DELETE /user
    #     """
    #     _session.delete(_session.query(User).get(_user_id))
    #     return jsonify('OK')


# class UserToolsApi():
    # """
    # User tools API
    # """
    # @staticmethod
    # @call_in_transaction
    # def check_email_exists(email: str, _session=None):
    #     """
    #     GET /user-tools/check-email-exists/<email>

    #     returns "true" if given email exists.
    #     no email validation
    #     """
    #     return jsonify('true') if _session.query(_session.query(User).filter(
    #         User.email == email).exists()).scalar() else jsonify('false')

