# There is some settings for tornado web

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = {
    "ENGINE": "mysqlconnector",
    "NAME": "",
    "USER": "",
    "PASSWORD": "",
    "PORT": 3306,
    "HOST": "localhost",
}

settings = {
    "template_path": "%s/%s" % (BASE_DIR, "templates"),
    "debug": True,
}
