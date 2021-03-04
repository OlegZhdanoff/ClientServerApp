import time
import json


ENCODING = 'utf-8'
MAX_MSG_SIZE = 640


def send_json(func):
    def inner(*args, **kwargs):
        return json.dumps(func(*args, **kwargs)).encode(ENCODING)
    return inner


class Client:
    def __init__(self, account_name, password, status):
        self.account_name = account_name
        self.password = password
        self.status = status

    @send_json
    def authenticate(self):
        return {
            "action": "authenticate",
            "time": time.time(),
            "user": {
                    "account_name":  self.account_name,
                    "password":      self.password
            }
        }

    @send_json
    def disconnect(self):
        return {
            "action": "quit"
        }

    @send_json
    def presence(self):
        return {
            "action": "presence",
            "time": time.time(),
            "type": self.status,
            "user": {
                    "account_name":  self.account_name,
                    "password":      self.password
            }
        }

    def action_handler(self, action, **kwargs):
        if action == 'probe':
            return self.presence()