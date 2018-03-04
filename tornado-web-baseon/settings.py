# There is some settings for tornado web

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

settings = {
    "template_path": "%s/%s" % (BASE_DIR, "templates"),
    "debug": True,
}
