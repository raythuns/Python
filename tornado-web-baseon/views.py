# Views here.

from source.components.base import BaseHandler


class HomeHandler(BaseHandler):
    def get(self):
        self.render("sample.html")
