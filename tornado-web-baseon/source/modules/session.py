import uuid
import hashlib

from source.modules.lib.session_sqlalchemy import (
    add_session, set_session, del_session, init_session)
from datetime import datetime, timedelta
from collections import OrderedDict


class Session:
    container = OrderedDict()

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
        return self.get_instance(session_id)

    def get_instance(self, session_id):
        if not session_id:
            return
        if isinstance(session_id, bytes):
            session_id = session_id.decode('utf-8')
        if not self._promise_exist(session_id):
            return
        data = dict(self.container[session_id][1])
        return SessionInstance(self, session_id, data,
                               self.container[session_id][0])

    def merge_instance(self, instance):
        if isinstance(instance, SessionInstance):
            s_id = instance.id
            if not self._promise_exist(s_id):
                return
            if len(instance.change):
                    self.container[s_id][1].update(instance.change)
            if len(instance.delete):
                for k in instance.delete:
                    del self.container[s_id][1][k]
            if instance.expire != self.container[s_id][0] and \
                    instance.expire > datetime.now():
                self.container[s_id] = (instance.expire,
                                        self.container[s_id][1])
                expire_date = instance.expire
            else:
                expire_date = None
            if len(instance.change) or len(instance.delete):
                set_session(self.db, s_id, self.container[s_id][1],
                            expire_date)
            elif expire_date:
                set_session(self.db, s_id, expire_date=expire_date)

    def destroy_instance(self, instance):
        if isinstance(instance, SessionInstance):
            s_id = instance.id
            del_session(self.db, s_id)
            if s_id in self.container.keys():
                del self.container[s_id]

    def _promise_exist(self, session_id):
        if session_id in self.container.keys():
            if self.container[session_id][0] <= datetime.now():
                del self.container[session_id]
                del_session(self.db, session_id)
                return False
            self.container.move_to_end(session_id)
            return True
        else:
            find = init_session(self.db, session_id)
            if not find:
                return False
            if len(self.container) > 1000:
                self.container.popitem(False)
            self.container[session_id] = find
            return True

    @staticmethod
    def _get_random_md5():
        u = uuid.uuid1()
        h = hashlib.md5(u.bytes)
        return h.hexdigest()


class SessionInstance:
    def __init__(self, session, session_id,
                 session_data, session_expire):
        self.session = session
        self.id = session_id
        self.data = session_data
        self.expire = session_expire
        self.change = {}
        self.delete = set()

    def get(self, key):
        try:
            rtn = self.change[key]
        except KeyError:
            rtn = self.data[key]
        return rtn

    def set(self, key, value):
        self.change[key] = value

    def remove(self, key):
        if key in self.change.keys():
            self.change.pop(key)
        elif key in self.data.keys():
            self.delete.add(key)

    def destroy(self):
        self.session.destroy_instance(self)

    def close(self):
        self.session.merge_instance(self)

    def __del__(self):
        self.close()
