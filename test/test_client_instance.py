import pytest
from freezegun import freeze_time

from server.server import *
from client.client import Client
import services
import json

ADDR = '127.0.0.1'


@pytest.fixture
def server_create():
    try:
        print("create Server Instance")
        serv = Server()
        serv.clients.setdefault(ADDR, Client('ivanov', '123', 'disconnected'))
        yield serv
    finally:
        del serv
        print('drop Server Instance')


@freeze_time("2012-01-14")
@pytest.fixture
def client_messages(server_create):
    try:
        print("fill message dict with data")
        yield {
            'authenticate': {
                "action": "authenticate",
                "time": time.time(),
                "user": {
                    "account_name": server_create.clients[ADDR].username,
                    "password": server_create.clients[ADDR].password
                }
            },
            'quit': {
                "action": "quit"
            },
            'presence': {
                "action": "presence",
                "time": time.time(),
                "type": server_create.clients[ADDR].status,
                "user": {
                    "account_name": server_create.clients[ADDR].username,
                    "password": server_create.clients[ADDR].password
                }
            }
        }
    finally:
        print("drop message dict")


def test_check_pwd(server_create, client_messages):
    assert server_create.check_pwd(server_create.clients[ADDR], client_messages['authenticate']['user']) == 200


def test_check_pwd_wrong(server_create):
    assert server_create.check_pwd(server_create.clients[ADDR],
                                   {
                                        "account_name": server_create.clients[ADDR].username,
                                        "password": 'wrong password'
                                    }) == 402


@freeze_time("2012-01-14")
def test_authenticate_200(server_create, client_messages):
    assert server_create.authenticate(client_messages['authenticate']['user'], ADDR) == json.dumps({
                "response": 200,
                "time": time.time(),
                "alert": 'добро пожаловать в чат'
            }).encode(services.ENCODING)


@freeze_time("2012-01-14")
def test_authenticate_402_wrong_pwd(server_create):
    assert server_create.authenticate({
        "account_name": server_create.clients[ADDR].username,
        "password": 'wrong password'
    }, ADDR) == json.dumps({
                "response": 402,
                "time": time.time(),
                "error": "This could be wrong password or no account with that name"
            }).encode(services.ENCODING)


@freeze_time("2012-01-14")
def test_authenticate_402_wrong_user(server_create):
    assert server_create.authenticate({
        "account_name": 'wrong username',
        "password": server_create.clients[ADDR].password
    }, ADDR) == json.dumps({
                "response": 402,
                "time": time.time(),
                "error": "This could be wrong password or no account with that name"
            }).encode(services.ENCODING)


@freeze_time("2012-01-14")
def test_authenticate_409_already_connected(server_create, client_messages):
    server_create.clients[ADDR].status = 'online'
    assert server_create.authenticate(client_messages['authenticate']['user'], ADDR) == json.dumps({
                "response": 409,
                "time": time.time(),
                "error": "Someone is already connected with the given user name"
            }).encode(services.ENCODING)


@freeze_time("2012-01-14")
def test_probe(server_create):
    assert server_create.probe() == json.dumps({
                "action": "probe",
                "time": time.time(),
            }).encode(services.ENCODING)
