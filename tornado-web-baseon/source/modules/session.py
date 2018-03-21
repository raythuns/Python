import uuid
import hashlib

from source.modules.lib.session_sqlalchemy import (
    add_session, set_session, del_session, init_session)
from datetime import datetime, timedelta


class Session:
    container = {}

    def __init__(self, db):
        self.db = db

    def create(self, info=None, expire_day=30):
        if not info:
            info = {}
        elif not isinstance(info, dict):
            raise ValueError("Must a dict or None.")
        session_id = self._get_random_md5()
        expire_date = datetime.now() + timedelta(days=expire_day)
        self.container[session_id] = (expire_date, info)
        add_session(self.db, session_id, info, expire_date)
        return session_id

    def remove(self, session_id):
        session_id = session_id.decode('utf-8')
        if session_id in self.container.keys():
            del_session(self.db, session_id)
            self.container.pop(session_id)

    def set(self, session_id, info):
        session_id = session_id.decode('utf-8')
        if not isinstance(info, dict):
            raise ValueError("Must a dict")
        if session_id in self.container.keys():
            set_session(self.db, session_id, info)
            return True
        else:
            find = init_session(self.db, session_id)
            if find:
                find[1] = info
                self.container[session_id] = find
                set_session(self.db, session_id, info)
            else:
                return False

    def get(self, session_id):
        if not session_id:
            return
        session_id = session_id.decode('utf-8')
        if session_id in self.container.keys():
            return self.container[session_id][1]
        else:
            find = init_session(self.db, session_id)
            if find:
                self.container[session_id] = find
                return find[1]

    @staticmethod
    def _get_random_md5():
        u = uuid.uuid1()
        h = hashlib.md5(u.bytes)
        return h.hexdigest()
