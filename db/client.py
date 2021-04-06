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
        return f'<Client(id={self.id}, login={self.login}, password={self.password}, status={self.status})>'


class ClientStorage:

    def __init__(self, session):
        self._session = session

    def add_client(self, login, password):
        try:
            # with self._session.begin():
            self._session.add(Client(login=login, password=password, status='disconnected'))
            self._session.commit()
        except IntegrityError as e:
            raise ValueError('login must be unique') from e

    def get_client(self, login, password):
        stmt = exists().where(and_(Client.login == login, Client.password == password))
        # print(stmt)
        return self._session.query(Client).filter(stmt).first()

    def set_status(self, client):

        try:
            # with self._session.begin():
            cl = self.get_client(client.login, client.password)
            cl.status = client.status
            self._session.commit()
                # self._session.add(Client(login=client.login, password=client.password, status='disconnected'))
        except IntegrityError as e:
            raise ValueError('login must be unique') from e

