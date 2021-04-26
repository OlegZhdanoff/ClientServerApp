import bcrypt as bcrypt
from icecream import ic
from sqlalchemy import and_, exists, Column, Integer, String, Boolean
from sqlalchemy.exc import IntegrityError
import icecream
from sqlalchemy.orm import relationship

from db.base import Base
from log.log_config import log_config

logger = log_config('ClientStorage', 'database.log')


class Client(Base):
    __tablename__ = 'Client'
    id = Column(Integer, primary_key=True)
    login = Column(String(20), unique=True)
    password = Column(String(100))
    is_admin = Column(Boolean, default=False)
    status = Column(String(20))

    Contacts = relationship("Contacts", order_by="Contacts.id", back_populates="Client")
    Message = relationship("Message", order_by="Message.id", back_populates="Client")
    # ClientHistory = relationship("ClientHistory", order_by="ClientHistory.id", back_populates="Client")

    def __repr__(self):
        return f'<Client(id={self.id}, login={self.login}, password={self.password}, status={self.status})>'


class ClientStorage:

    def __init__(self, session):
        self._session = session

    def add_client(self, login, password, is_admin=False):
        try:
            # with self._session.begin():
            hashAndSalt = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            self._session.add(Client(login=login, password=hashAndSalt, status='disconnected', is_admin=is_admin))
            self._session.commit()
            logger.info(f'client {login} was added to DB')
        except IntegrityError as e:
            raise ValueError('login must be unique') from e

    def auth_client(self, login, password):
        cl = self.get_client(login)
        try:
            if cl:
                if bcrypt.checkpw(password.encode(), cl.password):
                    return cl
                else:
                    return False
            else:
                return -1
        except Exception as e:
            ic(e)
            return False

    def get_client(self, login):
        return self._session.query(Client).filter_by(login=login).first()

    def filter_clients(self, pattern):
        res = []
        for user in self._session.query(Client.login).filter(Client.login.like(f'%{pattern}%')):
            print(type(user[0]))
            print(user[0])
            res.append(user[0])
        return res

    def set_status(self, client, status):
        # print('====== set_status()===========\n', client)
        # with self._session.begin():
        # cl = self.get_client(client.login, client.password)
        # print('====== set_status() before===========\n', cl)
        client.status = status
        self._session.commit()
        # print('====== set_status() result===========\n', cl)
        # self._session.commit()

    def get_all(self):
        return self._session.query(Client.login, Client.password, Client.status).all()

