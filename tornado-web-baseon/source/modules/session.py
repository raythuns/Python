import uuid

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
        session_id = self._get_random_id()
        expire_date = datetime.now() + timedelta(days=expire_day)
        self.container[session_id] = (expire_date, info)
        add_session(self.db, session_id, info, expire_date)
        return self.get_instance(session_id)

    def get_instance(self, session_id_ndor_version):
        if not session_id_ndor_version:
            return
        if isinstance(session_id_ndor_version, bytes):
            session_id_ndor_version = session_id_ndor_version.decode('utf-8')
        session_id = session_id_ndor_version[:32]
        if not self._ensure_exist(session_id):
            return
        if len(session_id_ndor_version) > 33:
            version = int(session_id_ndor_version[33:])
            if 'v' in self.container[session_id][1] and \
               self.container[session_id][1]['v'] < version:
                self._load_or_reload(session_id)
                self.container[session_id][1]['v'] = version
        data = dict(self.container[session_id][1])
        return SessionInstance(self, session_id, data,
                               self.container[session_id][0])

    def merge_instance(self, instance):
        if isinstance(instance, SessionInstance):
            s_id = instance.id
            if not self._ensure_exist(s_id):
                return
            if len(instance.delete):
                for k in instance.delete:
                    del self.container[s_id][1][k]
            if len(instance.change):
                self.container[s_id][1].update(instance.change)
            if instance.new_expire:
                self.container[s_id] = (instance.new_expire,
                                        self.container[s_id][1])
            if len(instance.change) or len(instance.delete):
                set_session(self.db, s_id, self.container[s_id][1],
                            instance.new_expire)
            elif instance.new_expire:
                set_session(self.db, s_id,
                            expire_date=instance.new_expire)

    def destroy_instance(self, instance):
        if isinstance(instance, SessionInstance):
            s_id = instance.id
            del_session(self.db, s_id)
            if s_id in self.container.keys():
                del self.container[s_id]

    def _ensure_exist(self, session_id):
        if session_id in self.container.keys():
            if self.container[session_id][0] <= datetime.now():
                del self.container[session_id]
                del_session(self.db, session_id)
                return False
            self.container.move_to_end(session_id)
            return True
        else:
            self._load_or_reload(session_id)

    def _load_or_reload(self, session_id):
        find = init_session(self.db, session_id)
        if not find:
            return False
        self.container[session_id] = find
        if len(self.container) > 1000:
            self.container.popitem(False)
        return True

    @staticmethod
    def _get_random_id():
        u = uuid.uuid1()
        return u.hex


class SessionInstance:
    def __init__(self, session, session_id,
                 session_data, session_expire):
        self.session = session
        self.id = session_id
        self.data = session_data
        self.expire = session_expire
        self.new_expire = None
        self.change = {}
        self.delete = set()
        self.use = True

    def get(self, key):
        try:
            return self.change[key]
        except KeyError:
            if key not in self.delete:
                try:
                    return self.data[key]
                except KeyError:
                    return

    def set(self, key, value):
        self.change[key] = value

    def remove(self, key):
        if key in self.change.keys():
            self.change.pop(key)
        if key in self.data.keys():
            self.delete.add(key)

    def reset_expire(self, expire_day=30):
        self.new_expire = datetime.now() + timedelta(days=expire_day)

    def sign_v(self):
        if self.use and (len(self.change) or len(self.delete)):
            if 'v' in self.data:
                v = self.data['v'] + 1
            else:
                v = 0
            self.set('v', v)
            if self.new_expire:
                expire = self.new_expire
            else:
                expire = self.expire
            expire_day = int((
                expire - datetime.now()).total_seconds()) / 86400
            rtn = ('%s|%d' % (self.id, v), expire_day)
        else:
            rtn = None
        self.close()
        return rtn

    def destroy(self):
        self.use and (self.session.destroy_instance(self)
                      or self._not_use())

    def close(self):
        self.use and (self.session.merge_instance(self)
                      or self._not_use())

    def _not_use(self):
        self.use = False

    def __del__(self):
        self.close()
