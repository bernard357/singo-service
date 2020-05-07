import datetime
from flask import Flask
import json
import jwt
from pytest import fixture, mark, raises as py_raises

from api_handlers import Handlers


pytestmark = mark.api


@fixture
def _api():
    app = Flask('for_test')
    handlers = Handlers()
    handlers.register_handlers(app)
    with app.app_context():
        yield handlers


class Fault:
    def __init__(self, message):
        self.description = message
        self.code = 500
        self.name = 'Some Error'

    def get_response(self):
        class Response():
            pass

        return Response()


def test_bad_request_error(_api):
    response, status_code = _api.bad_request_error(Fault('some fault'))
    assert status_code == 400
    assert response.mimetype == 'application/json'
    item = json.loads(response.data.decode().strip())
    assert item['code'] == 400
    assert item['name'] == 'Bad Request'
    assert item['description'] == 'some fault'


def test_forbidden_error(_api):
    response, status_code = _api.forbidden_error(Fault('some fault'))
    assert status_code == 403
    assert response.mimetype == 'application/json'
    item = json.loads(response.data.decode().strip())
    assert item['code'] == 403
    assert item['name'] == 'Forbidden'
    assert item['description'] == 'some fault'


def test_not_found_error(_api):
    response, status_code = _api.not_found_error(Fault('some fault'))
    assert status_code == 404
    assert response.mimetype == 'application/json'
    item = json.loads(response.data.decode().strip())
    assert item['code'] == 404
    assert item['name'] == 'Not Found'
    assert item['description'] == 'some fault'


def test_internal_server_error(_api):
    response, status_code = _api.internal_server_error(Fault('some fault'))
    assert status_code == 500
    assert response.mimetype == 'application/json'
    item = json.loads(response.data.decode().strip())
    assert item['code'] == 500
    assert item['name'] == 'Internal Server Error'
    assert item['description'] == 'some fault'

def test_http_error(_api):
    response = _api.http_error(Fault('some fault'))
    assert response.content_type == 'application/json'
    item = json.loads(response.data.strip())
    assert item['code'] == 500
    assert item['name'] == 'Some Error'
    assert item['description'] == 'some fault'
