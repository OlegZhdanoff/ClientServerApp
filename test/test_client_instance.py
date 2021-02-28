import pytest

from server.client_instance import *


@pytest.fixture
def client_create():
    try:
        print("create Client Instance")
        ci = ClientInstance('testUser', '123', 'online')
        yield ci
    finally:
        del ci
        print('drop Client Instance on server')


@pytest.fixture
def client_messages(client_create):
    try:
        print("fill message dict with data")
        yield {
            'authenticate': {
                "action": "authenticate",
                "time": time.time(),
                "user": {
                    "account_name": client_create.username,
                    "password": client_create.password
                }
            },
            'quit': {
                "action": "quit"
            },
            'presence': {
                "action": "presence",
                "time": time.time(),
                "type": client_create.status,
                "user": {
                    "account_name": client_create.username,
                    "password": client_create.password
                }
            }
        }
    finally:
        print("drop message dict")


def test_check_pwd(client_create, client_messages):
    assert client_create.check_pwd(client_messages['authenticate']['user']) == 200


def test_check_pwd_wrong(client_create):
    assert client_create.check_pwd({
        "account_name": client_create.username,
        "password": 'wrong password'
    }) == 402


def test_authenticate_200(client_create, client_messages):
    assert client_create.authenticate(client_messages['authenticate']['user']) == json.dumps({
                "response": 200,
                "time": time.time(),
                "alert": 'добро пожаловать в чат'
            }).encode(ENCODING)


def test_authenticate_402_wrong_pwd(client_create):
    assert client_create.authenticate({
        "account_name": client_create.username,
        "password": 'wrong password'
    }) == json.dumps({
                "response": 402,
                "time": time.time(),
                "error": "This could be wrong password or no account with that name"
            }).encode(ENCODING)


def test_authenticate_402_wrong_user(client_create):
    assert client_create.authenticate({
        "account_name": 'wrong username',
        "password": client_create.password
    }) == json.dumps({
                "response": 402,
                "time": time.time(),
                "error": "This could be wrong password or no account with that name"
            }).encode(ENCODING)


def test_probe(client_create):
    assert client_create.probe() == json.dumps({
                "action": "probe",
                "time": time.time(),
            }).encode(ENCODING)
