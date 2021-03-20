import pytest
from freezegun import freeze_time
import services
import json
from client.client import *


@pytest.fixture
def client_create():
    try:
        print("create Client")
        cl = Client('testUser', '123', 'online')
        yield cl
    finally:
        del cl
        print('drop Client')


@freeze_time("2012-01-14")
def test_authenticate(client_create):
    assert client_create.authenticate() == json.dumps({
                "action": "authenticate",
                "time": time.time(),
                "user": {
                    "account_name":  client_create.account_name,
                    "password":      client_create.password
                }
            }).encode(services.ENCODING)


def test_disconnect(client_create):
    assert client_create._close() == json.dumps({
                "action": "quit"
            }).encode(services.ENCODING)


@freeze_time("2012-01-14")
def presence(client_create):
    assert client_create._close() == json.dumps({
                "action": "presence",
                "time": time.time(),
                "type": client_create.status,
                "user": {
                        "account_name":  client_create.account_name,
                        "password":      client_create.password
                }
            }).encode(services.ENCODING)


@freeze_time("2012-01-14")
def test_action_handler_probe(client_create):
    assert client_create.action_handler('probe') == json.dumps({
                "action": "presence",
                "time": time.time(),
                "type": client_create.status,
                "user": {
                        "account_name":  client_create.account_name,
                        "password":      client_create.password
                }
            }).encode(services.ENCODING)
