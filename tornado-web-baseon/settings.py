# There is some settings for tornado web

import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


with open("%s/%s" % (BASE_DIR, "config/database.json"), 'rt') as f:
    DATABASE = json.load(f)

settings = {
    "template_path": "%s/%s" % (BASE_DIR, "templates"),
    "debug": True,
}
