# Views here.

from tornado.web import RequestHandler


class HomeHandler(RequestHandler):
    def get(self):
        self.render("sample.html")
