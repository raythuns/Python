from source.modules.orm import Model
from sqlalchemy import Column, String, Text, DateTime


class TornadoSession(Model):
    __tablename__ = 'tornado_session'

    session_id = Column(String(32), primary_key=True)
    session_data = Column(Text, nullable=False)
    expire_date = Column(DateTime, nullable=False)
