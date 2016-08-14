
import json

from tornado.web import RequestHandler, Application

from app.model.model import db


class Handler(RequestHandler):
    def jsonify(self, doc):
        if '_id' in doc:
            doc['id'] = str(doc.pop('_id'))
        return json.dumps(doc, indent=4, sort_keys=True) + '\n'

    async def jsonify_list(self, docs):
        data = []
        async for doc in docs:
            if '_id' in doc:
                doc['id'] = str(doc.pop('_id'))
            data.append(doc)
        return json.dumps(data, indent=4, sort_keys=True)

    def req_json(self):
        return json.loads(self.request.body.decode('utf8'))


class MainHandler(Handler):
    async def get(self):
        docs = db.users.find({}, {'name': 1})
        data = await self.jsonify_list(docs)
        self.write(data)

    async def post(self):
        user_id = await db.users.insert(self.req_json())
        self.write(str(user_id))


def init(app: Application):
    app.add_handlers(
        r'.*',
        [
            (r'/foo', MainHandler)
        ])
