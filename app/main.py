""" Main App Module """

import logging
import tornado.web

app = None


def init():
    """ init app """
    global app
    app = tornado.web.Application(debug=True)

    #
    #  log
    #
    logging.basicConfig(
        format='%(asctime)s %(levelname).1s[%(module)s:%(lineno)d]: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.DEBUG)
    logging.debug('initializing app. pid: %d', os.getpid())

    # init mongodb
    from app.model import model
    model.init('tornado-test-dev')

    # init rest
    from app.rest import rest
    rest.init(app)

    return app


if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.getcwd())

    app = init()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
