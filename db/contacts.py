from sqlalchemy import and_, exists, Column, Integer, String, ForeignKey
import icecream
from sqlalchemy.orm import relationship

from db.base import Base
from db.client import Client


class Contacts(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("Client.id"))
    client_id = Column(Integer)

    client = relationship("Client", back_populates="Contacts")

    def __repr__(self):
        return f'<Contact(id={self.id}, owner_id={self.owner_id}, client_id={self.client_id})>'


class ContactStorage:

    def __init__(self, session):
        self._session = session

    def add_contact(self, owner, client_login):
        client = self._session.query(Client).filter_by(login=client_login).first()
        if client and not self.get_contact(owner, client_login):
            self._session.add(Contacts(owner.id, client.id))
            self._session.commit()
        else:
            raise ValueError(f'client <{client_login}> not found')

    def get_contact(self, owner, client_login):
        client = self._session.query(Client).filter_by(login=client_login).first()
        if client:
            contact = self._session.query(Contacts).filter(and_(owner_id=owner.id, client_id=client.id)).first()
            if contact:
                return contact
            else:
                return False
        else:
            raise ValueError(f'Client <{client_login}> not found')

    def del_contact(self, owner, client_login):
        contact = self.get_contact(owner, client_login)
        if contact:
            self._session.delete(contact)
            self._session.commit()
        else:
            raise ValueError(f'contact <{owner.login}> - <{client_login}> not found')
