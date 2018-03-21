from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sys

sys.path.append('../../')

from settings import DATABASE

Model = declarative_base()

_ = DATABASE

engine = create_engine('mysql+%s://%s:%s@%s:%d/%s' % (
    _['ENGINE'], _['USER'], _['PASSWORD'],
    _['HOST'], _['PORT'], _['NAME']))

DBSession = sessionmaker(bind=engine)
