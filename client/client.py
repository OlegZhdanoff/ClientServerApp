import time
from queue import Queue, Empty

import structlog

from log.log_config import log_config, log_default
from services import serializer
from messages import *

logger = log_config('client', 'client.log')


class Client:
    def __init__(self, account_name, password, status='disconnected'):
        self.username = account_name
        self.password = password
        self.status = status
        self.data_queue = Queue()

    @log_default(logger)
    def __eq__(self, other):
        return self.username == other.username

    def __str__(self):
        return self.username

    @log_default(logger)
    def set_status(self, status):
        self.status = status

    @log_default(logger)
    def feed_data(self, data):
        self.data_queue.put(data)

    # @log_default(logger)
    def get_data(self):
        try:
            data = self.data_queue.get_nowait()
            self.data_queue.task_done()
            return data
        except Empty as e:
            pass

    @log_default(logger)
    @serializer
    def authenticate(self):
        return Authenticate(username=self.username, password=self.password)

    @log_default(logger)
    @serializer
    def disconnect(self):
        return Quit()

    @log_default(logger)
    @serializer
    def presence(self):
        return Presence(username=self.username, status=self.status)

    @log_default(logger)
    @serializer
    def send_message(self, to, text):
        return Msg(to=to, from_=self.username, text=text)

    @log_default(logger)
    @serializer
    def join(self, room):
        return Join(room=room)

    @log_default(logger)
    @serializer
    def leave(self, room):
        return Leave(room=room)

    @log_default(logger)
    def action_handler(self, msg):
        if isinstance(msg, Probe):
            self.feed_data(self.presence())
        elif isinstance(msg, Msg):
            self.on_msg(msg)
        elif isinstance(msg, Response):
            self.response_processor(msg)
        else:
            logger.warning(f"Unknown server's message {msg}")
            self.close()

    @log_default(logger)
    def response_processor(self, msg: Response):
        print(time.ctime(time.time()) + f': {msg.alert}')
        if msg.response == 200:
            return 'You are connected...'
        elif msg.response == 402:
            return 'Your password is incorrect'
        else:
            logger.warning(f'Unknown response {msg}')
            return f'Unknown response {msg}'

    @log_default(logger)
    def on_msg(self, msg):
        print(time.ctime(time.time()) + f': {msg.from_}: {msg.text}')

    @log_default(logger)
    def close(self):
        self.feed_data('close')
