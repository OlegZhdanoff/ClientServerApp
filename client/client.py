import time
import json
import structlog

from log.log_config import log_config
from settings import send_json

logger = log_config('client', 'client.log')


class Client:
    def __init__(self, account_name, password, status='disconnected'):
        self.account_name = account_name
        self.password = password
        self.status = status

    def __eq__(self, other):
        return self.account_name == other.account_name

    def __str__(self):
        return self.account_name

    def set_status(self, status):
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
