import datetime

from sqlalchemy import and_, Column, Integer, ForeignKey, DateTime, String, or_
from sqlalchemy.orm import relationship

from db.base import Base
from db.client import Client
from log.log_config import log_config

logger = log_config('Messages', 'database.log')


class Message(Base):
    __tablename__ = 'Message'
    id = Column(Integer, primary_key=True)
    from_id = Column(Integer, ForeignKey("Client.id"))
    to_id = Column(Integer)
    when = Column(DateTime)
    message = Column(String(500))

    Client = relationship("Client", back_populates="Message")

    def __repr__(self):
        return f'<Message(id={self.id}, from_id={self.from_id}, to_id={self.to_id}, when={self.when}, ' \
               f'message={self.message})>'


class MessageStorage:

    def __init__(self, session, owner):
        self._session = session
        self.owner = owner
        self.logger = logger.bind(owner=owner.login)

    def add_message(self, recipient: Client, msg: str, when=datetime.datetime.now()):
        self._session.add(Message(from_id=self.owner.id, to_id=recipient.id, when=when,
                                  message=msg))
        self._session.commit()

    def get_from_owner_messages(self):
        return self._session.query(Message).filter_by(from_id=self.owner.id).all()

    def get_to_user_messages(self, user: Client):
        return self._session.query(Message).filter(and_(Message.from_id == self.owner.id, Message.to_id ==
                                                        user.id)).all()

    def get_chat_msg(self, user: Client):
        return self._session\
                .query(Message.when, Message.message, Client.login)\
                .join(Client)\
                .filter(Client.id == Message.from_id)\
                .filter(or_(and_(Message.from_id == user.id, Message.to_id == self.owner.id),
                            and_(Message.from_id == self.owner.id, Message.to_id == user.id)))\
                .all()

    def get_to_owner_msg_from_time(self, tm: datetime):
        res = None
        try:
            res = self._session\
                .query(Message.when, Message.message, Client.login)\
                .join(Client)\
                .filter(Client.id == Message.from_id)\
                .filter(and_(Message.when > tm, Message.to_id == self.owner.id))\
                .all()
        except Exception:
            logger.exception('get_to_owner_msg_from_time ERROR')
        return res
