from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from GeekChat.db import Base
from GeekChat.db.client import Client


class ClientHistory(Base):
    __tablename__ = 'ClientHistory'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("Client.id"))
    ip_address = Column(String(4 + 4 + 4 + 3), unique=False)
    when = Column(DateTime)

    Client = relationship("Client", backref="history")

    def __repr__(self):
        return f'<Client(id={self.id}, login={self.ip_address}, password={self.password})>'


class ClientHistoryStorage:

    def __init__(self, session, owner):
        self._session = session
        self.owner = owner

    def add_record(self, address, tm):
        self._session.add(ClientHistory(client_id=self.owner.id, ip_address=address, when=tm))
        self._session.commit()

    def get_history(self):
        res = []
        query_res = self._session.query(Client.login, ClientHistory.ip_address, ClientHistory.when) \
            .join(Client.history).filter(ClientHistory.client_id == self.owner.id).all()
        for record in query_res:
            res.append((record[0], record[1], record[-1].strftime("%m/%d/%Y, %H:%M:%S")))
        return res
