import time
from dataclasses import dataclass


@dataclass
class Presence:
    user: dict
    action: str = 'presence'
    time: float = time.time()
    type: str = 'status'


@dataclass
class Authenticate:
    user: dict
    action: str = 'authenticate'
    time: float = time.time()


@dataclass
class Response:
    response: int = 200
    time: float = time.time()
    alert: str = 'alert'


@dataclass
class Quit:
    action: str = 'quit'


@dataclass
class Probe:
    action: str = 'probe'
    time: float = time.time()


@dataclass
class Msg:
    action: str = 'msg'
    time: float = time.time()
    to: str = 'user'
    _from: str = 'user'
    message: str = 'message'


@dataclass
class Join:
    action: str = 'join'
    time: float = time.time()
    room: str = '#room_name'


@dataclass
class Leave:
    action: str = 'leave'
    time: float = time.time()
    room: str = '#room_name'
