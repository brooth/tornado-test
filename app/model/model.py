"""
Manage mongodb connection and model layer
"""

import motor.motor_tornado

client = None
db = None


def init(db_name):
    """ initializes mongo db connection """
    global client, db
    client = motor.motor_tornado.MotorClient()
    db = client[db_name]
