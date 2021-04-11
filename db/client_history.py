from sqlalchemy import and_, exists, Column, Integer, String, DateTime
from sqlalchemy.exc import IntegrityError

from db.base import Base


class ClientHistory(Base):
    __tablename__ = 'connect_history'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer)
    ip_address = Column(String(4 + 4 + 4 + 3), unique=False)
    when = Column(DateTime)

    def __repr__(self):
        return f'<Client(id={self.id}, login={self.ip_address}, password={self.password})>'


class ClientHistoryStorage:

    def __init__(self, session):
        self._session = session

    def add_record(self, client_id, address, tm):
        # with self._session.begin():
        self._session.add(ClientHistory(client_id=client_id, ip_address=address, when=tm))
        self._session.commit()
