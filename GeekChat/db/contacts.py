from sqlalchemy import and_, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from GeekChat.db.base import Base
from GeekChat.db.client import Client
from GeekChat.log.log_config import log_config

logger = log_config('Contacts', 'database.log')


class Contacts(Base):
    __tablename__ = 'Contacts'
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("Client.id"))
    client_id = Column(Integer)

    Client = relationship("Client", back_populates="Contacts")

    def __repr__(self):
        return f'<Contact(id={self.id}, owner_id={self.owner_id}, client_id={self.client_id})>'


class ContactStorage:

    def __init__(self, session, owner):
        self._session = session
        self.owner = owner
        self.logger = logger.bind(owner=owner.login)

    def add_contact(self, client_login):
        client, contact = self._get_contact(client_login)

        if client:
            if not contact:
                self._session.add(Contacts(owner_id=self.owner.id, client_id=client.id))
                self._session.commit()
                self.logger.info(f'contact <{client_login}> was added')
            else:
                self.logger.warning(f'client <{client_login}> in your contacts already')
                raise ValueError(f'client <{client_login}> in your contacts already')
        else:
            self.logger.warning(f'client <{client_login}> not found')
            raise ValueError(f'client <{client_login}> not found')

    def _get_contact(self, client_login):
        client = self._session.query(Client).filter_by(login=client_login).first()
        if self.owner.Contacts and client:
            contact = self._session.query(Contacts).filter(and_(Contacts.owner_id == self.owner.id,
                                                                Contacts.client_id == client.id)).first()
        else:
            contact = None
        return client, contact

    def del_contact(self, client_login):
        client, contact = self._get_contact(client_login)
        if contact:
            self._session.delete(contact)
            self._session.commit()
            self.logger.info(f'contact <{client_login}> was deleted')
        else:
            self.logger.warning(f'contact <{self.owner.login}> - <{client_login}> not found')
            raise ValueError(f'contact <{self.owner.login}> - <{client_login}> not found')

    def get_contacts(self):
        contacts = []
        for contact in self.owner.Contacts:
            # print(type(contact.client_id))
            # print(contact.client_id)
            contacts.append(self._session.query(Client).filter_by(id=contact.client_id).first().login)
        return contacts
