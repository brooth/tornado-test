
import tornado.web


def init():
    application = tornado.web.Application()

    # init rest
    from app.rest import rest
    rest.init(application)

    return application


if __name__ == "__main__":
    import sys, os
    sys.path.append(os.getcwd())

    app = init()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
