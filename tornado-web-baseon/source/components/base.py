from tornado.web import RequestHandler
from source.modules.orm import DBSession
from source.modules.session import Session


class BaseHandler(RequestHandler):
    def initialize(self):
        self.db = DBSession()
        self.session = Session(self.db)

    def on_finish(self):
        self.db.close()
