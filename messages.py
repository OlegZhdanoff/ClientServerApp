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

    def __json__(self):
        return {
            "action": self.action,
            "time": self.time,
            "user": {
                "account_name": self.username,
                "password": self.password
            }
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
            "error": self.alert
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
            "time": time.time(),
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