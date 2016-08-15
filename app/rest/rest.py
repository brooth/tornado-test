# pylint: disable=locally-disabled, invalid-name
""" Main REST API module """

import json
from logging import getLogger

from tornado.web import RequestHandler, Application, HTTPError

from app.rest.tools import jsonify

logger = getLogger()


class ErrorResponse(HTTPError):
    """ represents not OK response """
    def __init__(self, message, status_code=400, error_code=-1):
        super().__init__(reason=message, status_code=status_code)
        self.message = message
        self.error_code = error_code


class Handler(RequestHandler):
    # pylint: disable=locally-disabled, abstract-method
    """ Base API Handler """
    def error_response(self, message, status_code=400, error_code=-1):
        """ writes errror response as json """
        self.set_header('Content-Type', 'text/json')
        self.set_status(status_code, message)
        if error_code != -1:
            self.write(jsonify({
                "message": message,
                "error_code": error_code
            }))
        else:
            self.write(jsonify({
                "message": message
            }))

    def write_error(self, status_code, **kwargs):
        if "exc_info" in kwargs:
            ex = kwargs["exc_info"][1]
            if isinstance(ex, ErrorResponse):
                self.error_response(ex.message, status_code, ex.error_code)
            else:
                self.error_response(str(ex), status_code, -1)

    def read_json(self):
        """ reads json from request body """
        return json.loads(self.request.body.decode('utf8'))


def init(app: Application):
    """ initializes rest api """
    from app.rest.user_api import UserAPI

    app.add_handlers(r'.*', [
        (r'/users', UserAPI)
    ])
