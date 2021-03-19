import json
import time
from threading import Thread

import settings
from client.client_thread import SelectableQueue
from log.log_config import log_config, log_default
from settings import send_json

logger = log_config('shadow_client', 'client.log')


class ShadowUser(Thread):
    def __init__(self, sq_gui: SelectableQueue,  sq_client: SelectableQueue, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.daemon = True
        self.sq_gui = sq_gui
        self.sq_client = sq_client
        self.account_name = 'Shadow'
        self.name = 'ShadowUser'

    def run(self) -> None:
        print(1)
        while True:
            try:
                data = self.sq_gui.get()
                self.sq_gui.task_done()
                if not data == '':
                    data = data.decode(settings.ENCODING)
                    print(2, data)
                    msg_list = settings.get_msg_list(data)
                    if msg_list:
                        for data in msg_list:
                            msg = json.loads(data)
                            if "action" in msg:
                                self.action_handler(msg["action"], msg)
                else:
                    return
            except Exception as e:
                logger.exception(f'Error')

    @log_default(logger)
    def action_handler(self, action, msg):
        if action == 'msg':
            self.sq_client.put(self.send_message(msg['from'], f'hello {msg["from"]}'))

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