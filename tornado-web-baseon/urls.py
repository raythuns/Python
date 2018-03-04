# URL Configure

from tornado.web import url
import views

urls = [
    url(r"/", views.HomeHandler),
    ]
