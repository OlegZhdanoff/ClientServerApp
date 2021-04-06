from sqlalchemy import and_, exists, Column, Integer, String
from sqlalchemy.exc import IntegrityError

from db.base import Base


class Client(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    login = Column(String(20), unique=True)
    password = Column(String(100))
    status = Column(String(20))

    def __repr__(self):
        return f'<Client(id={self.id}, login={self.login}, password={self.password})>'


class ClientStorage:

    def __init__(self, session):
        self._session = session

    def add_client(self, login, password):
        try:
            with self._session.begin():
                self._session.add(Client(login=login, password=password, status='disconnected'))
        except IntegrityError as e:
            raise ValueError('login must be unique') from e

    def auth_client(self, login, password):
        stmt = exists().where(and_(Client.login == login, Client.password == password))
        return self._session.query(Client).filter(stmt).first()

