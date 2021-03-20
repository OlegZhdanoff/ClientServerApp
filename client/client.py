import time
from queue import Queue

import structlog

from log.log_config import log_config, log_default
from services import serializer

logger = log_config('client', 'client.log')


class Client:
    def __init__(self, account_name, password, status='disconnected'):
        self.account_name = account_name
        self.password = password
        self.status = status
        self.data_queue = Queue()

    @log_default(logger)
    def __eq__(self, other):
        return self.account_name == other.account_name

    def __str__(self):
        return self.account_name

    @log_default(logger)
    def set_status(self, status):
        self.status = status

    @log_default(logger)
    def feed_data(self, data):
        self.data_queue.put(data)

    @log_default(logger)
    @serializer
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
    @serializer
    def disconnect(self):
        return {
            "action": "quit"
        }

    @log_default(logger)
    @serializer
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
    @serializer
    def send_message(self, to, text):
        return {
            "action": "msg",
            "time": time.time(),
            "to": to,
            "from": self.account_name,
            "message": text
        }

    @log_default(logger)
    def action_handler(self, action, msg):
        if action == 'probe':
            return self.presence()
        elif action == 'msg':
            print(time.ctime(time.time()) + f': {msg["from"]}: {msg["message"]}')

    @log_default(logger)
    def response_processor(self, response, msg):
        if response == 200:
            print(time.ctime(time.time()) + f': {msg["alert"]}')
            return 'You are connected...'
        elif response == 402:
            return 'Your password is incorrect'

    @log_default(logger)
    def close(self):
        self.feed_data(None)
