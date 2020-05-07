import datetime
from flask import Flask
import json
import jwt
from pytest import fixture, mark, raises as py_raises
from urllib.parse import unquote
import werkzeug

from api_channel import Channel


@fixture
def _api():
    app = Flask(__name__)
    channel = Channel()
    channel.register_routes(app)
    with app.app_context(), app.test_request_context():
        yield channel


def test_init(_api):
    assert _api.prefix == ''


def test_record_life_cycle(_api):

    id = '01234567890-c01'
    record_version1 = dict(id=id, title='hello world', description='etc.')
    record_version2 = dict(id=id, title='another title')

    response = _api.post(payload=record_version1, persona='leader')
    assert response == ('', 201, {'Location': '/01234567890-c01'})

    response = _api.get(id=id)
    assert response.status_code == 200
    payload = json.loads(response.get_data().decode())
    record = payload['item']
    for key in record_version1.keys():
        assert record[key] == record_version1[key]

    with py_raises(werkzeug.exceptions.BadRequest):
        _api.put(id=None, payload=record_version2, persona='leader')

    response = _api.put(id=id, payload=record_version2, persona='leader')
    assert response == ('', 204)

    response = _api.get(id=id)
    assert response.status_code == 200
    payload = json.loads(response.get_data().decode())
    record = payload['item']
    for key in record_version2.keys():
        assert record[key] == record_version2[key]
    for key in record_version1.keys():
        assert key in record.keys()

    response = _api.delete(id=id, persona='leader')
    assert response == ('', 204)

    with py_raises(werkzeug.exceptions.NotFound):
        _api.get(id=id)


def test_versions_conflict(_api):

    id = 'versioned-c09'
    record_version1 = dict(id=id, title='version 1', version='alpha')
    record_version2 = dict(id=id, title='version 2', version='beta')
    record_version3 = dict(id=id, title='version 3', version='beta', previous_version='alpha')
    record_version4 = dict(id=id, title='version 4', version='gamma', previous_version='alpha')
    record_version5 = dict(id=id, title='version 5', version='delta', previous_version='beta')
    record_version6 = dict(id=id, title='version 6', version='delta', previous_version='delta')

    response = _api.put(id=id, payload=record_version1, persona='leader')
    assert response == ('', 204)

    with py_raises(werkzeug.exceptions.Conflict):
        _api.put(id=id, payload=record_version2, persona='leader')

    response = _api.put(id=id, payload=record_version3, persona='leader')
    assert response == ('', 204)

    with py_raises(werkzeug.exceptions.Conflict):
        _api.put(id=id, payload=record_version4, persona='leader')

    response = _api.put(id=id, payload=record_version5, persona='leader')
    assert response == ('', 204)

    response = _api.put(id=id, payload=record_version6, persona='leader')
    assert response == ('', 204)

    response = _api.get(id=id)
    payload = json.loads(response.get_data().decode())
    assert payload['item']['version'] == 'delta'

    response = _api.delete(id=id, persona='leader')
    assert response == ('', 204)


def test_record_maximum_size(_api):

    _api.record_maximum_size = 26

    with py_raises(werkzeug.exceptions.BadRequest):
        _api.post(payload={'title': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'},
                  persona='leader')

    with py_raises(werkzeug.exceptions.BadRequest):
        _api.put(id='fat',
                 payload={'title': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'},
                 persona='leader')


def test_index(_api):

    response = _api.index()
    chunk = json.loads(response.data.decode())
    assert len(chunk['items']) == 0
    token = unquote(chunk['next'])
    assert token == 'EOF'

    _api.page_size = 5
    for n in range(_api.page_size * 2 + 3):
        _api.store.write(id=f"id-{n + 1}", content=f"hello {n + 1}")

    response = _api.index()
    chunk = json.loads(response.data.decode())
    assert len(chunk['items']) == _api.page_size
    token = unquote(chunk['next'])
    assert token != 'EOF'


def test_page(_api):

    pages = 4

    _api.store.salt = 'hello world'
    for n in range(_api.page_size * (pages - 1) + 7):
        _api.store.write(id=f"id-{n + 1}", content=f"hello {n + 1}")

    token = None
    while token != 'EOF':
        response = _api.page(token=token)
        chunk = json.loads(response.data.decode())
        token = unquote(chunk['next'])
        if token.startswith('/page/'):
            token = token[len('/page/'):]
        pages -= 1
    assert pages == 0

    with py_raises(werkzeug.exceptions.NotFound):
        _api.page(token='EOF')

    response = _api.page(token=_api.store._encode_token(-235))
    chunk = json.loads(response.data.decode())
    print(chunk)
    assert len(chunk['items']) == _api.page_size
    token = unquote(chunk['next'])
    assert token != 'EOF'
