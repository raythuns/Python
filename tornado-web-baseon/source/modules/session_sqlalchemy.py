from source.modules.session_sqlalchemy_model import TornadoSession
from source.modules.orm import Session
import pickle
import base64


def _encode(data):
    s = pickle.dumps(data)
    return base64.b64encode(s).decode(encoding='utf-8')


def _decode(st):
    s = base64.b64decode(st.encode(encoding='utf-8'))
    return pickle.loads(s)


def add_session(session_id, session_data_dict, expire_date):
    ts = TornadoSession(session_id=session_id,
                        session_data=_encode(session_data_dict),
                        expire_date=expire_date)
    sess = Session()
    sess.add(ts)
    sess.commit()
    sess.close()


def set_session(session_id, session_data_dict):
    sess = Session()
    ret = sess.query(TornadoSession).\
        filter_by(session_id=session_id).first()
    ret.session_data = session_data_dict
    sess.commit()
    sess.close()


def del_session(session_id):
    sess = Session()
    ret = sess.query(TornadoSession).\
        filter_by(session_id=session_id).first()
    sess.delete(ret)
    sess.commit()
    sess.close()


def ini_session():
    ret = dict()
    sess = Session()
    for i in sess.query(TornadoSession).all():
        ret[i.session_id] =\
            (0, _decode(i.session_data))
    sess.close()
    return ret
