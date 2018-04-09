import pickle
import base64

from source.modules.lib.session_sqlalchemy_model import TornadoSession
from datetime import datetime


def _encode(data):
    s = pickle.dumps(data)
    return base64.b64encode(s).decode(encoding='utf-8')


def _decode(st):
    s = base64.b64decode(st.encode(encoding='utf-8'))
    return pickle.loads(s)


def add_session(db, session_id, session_data_dict, expire_date):
    ts = TornadoSession(session_id=session_id,
                        session_data=_encode(session_data_dict),
                        expire_date=expire_date)
    db.add(ts)
    db.commit()


def set_session(db, session_id, session_data_dict=None, expire_date=None):
    ret = db.query(TornadoSession).\
        filter_by(session_id=session_id).first()
    if session_data_dict:
        ret.session_data = _encode(session_data_dict)
    if expire_date:
        ret.expire_date = expire_date
    db.commit()


def del_session(db, session_id):
    ret = db.query(TornadoSession).\
        filter_by(session_id=session_id).first()
    db.delete(ret)
    db.commit()


def init_session(db, session_id):
    ret = db.query(TornadoSession).\
        filter_by(session_id=session_id).first()
    if ret:
        dn = datetime.now()
        if ret.expire_date <= dn:
            del_session(db, session_id)
            return
        return ret.expire_date, _decode(ret.session_data)
