# Run to start web server

import tornado.ioloop
import tornado.web

from settings import settings
from urls import urls


app = tornado.web.Application(urls, **settings)


if __name__ == "__main__":
    app.listen(80)
    tornado.ioloop.IOLoop.current().start()
