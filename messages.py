import datetime
import time
from dataclasses import dataclass


@dataclass
class Presence:
    action: str = 'presence'
    time: float = time.time()
    type: str = 'status'
    username: str = 'username'
    status: str = 'offline'

    def __json__(self):
        return {
            "action": self.action,
            "time": self.time,
            "type": self.type,
            "user": {
                    "account_name":  self.username,
                    "status":      self.status
            }
        }


@dataclass
class Authenticate:
    action: str = 'authenticate'
    time: float = time.time()
    username: str = 'username'
    password: str = 'password'
    result: bool = False
    alert: str = ''

    def __json__(self):
        return {
            "action": self.action,
            "time": self.time,
            "user": {
                "account_name": self.username,
                "password": self.password
            },
            "result": self.result,
            "alert": self.alert
        }


@dataclass
class Response:
    response: int = 200
    time: float = time.time()
    alert: str = 'alert'

    def __json__(self):
        return {
            "response": self.response,
            "time": self.time,
            "alert": self.alert
        }


@dataclass
class Quit:
    action: str = 'quit'

    def __json__(self):
        return {
            "action": self.action
        }


@dataclass
class Probe:
    action: str = 'probe'
    time: float = time.time()

    def __json__(self):
        return {
            "action": self.action,
            "time": self.time
        }


@dataclass
class Msg:
    action: str = 'msg'
    time: float = time.time()
    to: str = 'user'
    from_: str = 'user'
    text: str = 'message'

    def __json__(self):
        return {
            "action": self.action,
            "time": self.time,
            "to": self.to,
            "from": self.from_,
            "message": self.text
        }


@dataclass
class GetMessages:
    action: str = 'get_messages'
    time: float = time.time()
    from_: str = ''

    def __json__(self):
        return {
            "action": self.action,
            "time": self.time,
            "from_": self.from_,
        }


@dataclass
class Join:
    action: str = 'join'
    time: float = time.time()
    room: str = '#room_name'

    def __json__(self):
        return {
            "action": self.action,
            "time": self.time,
            "room": self.room
        }


@dataclass
class Leave:
    action: str = 'leave'
    time: float = time.time()
    room: str = '#room_name'

    def __json__(self):
        return {
            "action": self.action,
            "time": self.time,
            "room": self.room
        }


@dataclass
class GetContacts:
    action: str = 'get_contacts'
    time: float = time.time()
    contacts: tuple = ()
    login: str = ''

    def __json__(self):
        return {
            "action": self.action,
            "time": self.time,
            "contacts": self.contacts,
            "login": self.login
        }


@dataclass
class AddContact:
    action: str = 'add_contact'
    time: float = time.time()
    username: str = 'user'

    def __json__(self):
        return {
            "action": self.action,
            "time": self.time,
            "username": self.username
        }


@dataclass
class DelContact:
    action: str = 'del_contact'
    time: float = time.time()
    username: str = 'user'

    def __json__(self):
        return {
            "action": self.action,
            "time": self.time,
            "username": self.username
        }


@dataclass
class FilterClients:
    action: str = 'filter_clients'
    time: float = time.time()
    pattern: str = ''
    users: tuple = ()

    def __json__(self):
        return {
            "action": self.action,
            "time": self.time,
            "filter": self.pattern,
            "users": self.users
        }


@dataclass
class AdminGetUsers:
    action: str = 'admin_get_users'
    time: float = time.time()
    users: tuple = ()

    def __json__(self):
        return {
            "action": self.action,
            "time": self.time,
            "users": self.users
        }


@dataclass
class AdminGetHistory:
    action: str = 'admin_get_history'
    time: float = time.time()
    user: str = ''
    history: tuple = ()

    def __json__(self):
        return {
            "action": self.action,
            "time": self.time,
            "user": self.user,
            "history": self.history
        }


@dataclass
class SendKey:
    action: str = 'public_key'
    key: bytes = b''

    def __json__(self):
        return {
            "action": self.action,
            "key": self.key
        }
