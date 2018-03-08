import uuid
import hashlib

container = {}


class _Session:
    @staticmethod
    def create(info=None):
        if not info:
            info = {}
        elif not isinstance(info, dict):
            raise ValueError("Must a dict or None.")
        global container
        session_id = _Session._get_random_md5()
        container[session_id] = info
        return session_id

    @staticmethod
    def remove(session_id):
        session_id = session_id.decode('utf-8')
        global container
        if session_id in container.keys():
            container.pop(session_id)

    @staticmethod
    def set(session_id, info):
        session_id = session_id.decode('utf-8')
        if not isinstance(info, dict):
            raise ValueError("Must a dict")
        global container
        if session_id in container.keys():
            container[session_id] = info
            return True
        else:
            return False

    @staticmethod
    def get(session_id):
        session_id = session_id.decode('utf-8')
        if session_id in container.keys():
            return container[session_id]
        else:
            return {"user": None}

    @staticmethod
    def _get_random_md5():
        u = uuid.uuid1()
        h = hashlib.md5(u.bytes)
        return h.hexdigest()


session = _Session
