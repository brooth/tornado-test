# pylint: disable=locally-disabled, invalid-name
"""
Manage mongodb connection and model layer
"""

from logging import getLogger

import motor.motor_tornado

logger = getLogger()
client = None
db = None


def init(db_name):
    """ initializes mongo db connection """
    logger.debug('init model, db_name: %s', db_name)

    global client, db
    client = motor.motor_tornado.MotorClient()
    db = client[db_name]
