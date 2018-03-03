import tornado.ioloop
import tornado.web


class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("something.")


settings = {

}

app = tornado.web.Application([
    (r"/", HomeHandler),
    ], **settings)


if __name__ == "__main__":
    app.listen(80)
    tornado.ioloop.IOLoop.current().start()
