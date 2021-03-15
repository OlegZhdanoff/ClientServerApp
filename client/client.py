import time
import structlog

from log.log_config import log_config, log_default
from settings import send_json

logger = log_config('client', 'client.log')


class Client:
    def __init__(self, account_name, password, status='disconnected'):
        self.account_name = account_name
        self.password = password
        self.status = status

    @log_default(logger)
    def __eq__(self, other):
        return self.account_name == other.account_name

    def __str__(self):
        return self.account_name

    @log_default(logger)
    def set_status(self, status):
        self.status = status

    @log_default(logger)
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

    @log_default(logger)
    @send_json
    def disconnect(self):
        return {
            "action": "quit"
        }

    @log_default(logger)
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

    @log_default(logger)
    @send_json
    def send_message(self, to, text):
        return {
            "action": "msg",
            "time": time.time(),
            "to": to,
            "from": self.account_name,
            "message": text
        }

    @log_default(logger)
    def action_handler(self, action, **kwargs):
        if action == 'probe':
            return self.presence()
