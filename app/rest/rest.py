
import asyncio 

from tornado.web import RequestHandler, Application


class MainHandler(RequestHandler):
    def get(self):
        self.write("Hi there!")

        async def call():



def init(app: Application):
    app.add_handlers(
        r'.*',
        [
            (r'/foo', MainHandler)
        ])
