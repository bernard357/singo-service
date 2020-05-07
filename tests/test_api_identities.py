import datetime
from flask import Flask
import json
import jwt
from pytest import fixture, mark, raises as py_raises
from urllib.parse import unquote
import werkzeug

from api_identities import Identities


@fixture
def _api():
    app = Flask(__name__)
    identities = Identities()
    identities.register_routes(app)
    with app.app_context(), app.test_request_context():
        yield identities


def test_init(_api):
    pass


def test_post_malformed_request(_api):

    record = dict(password='P455w@rd',
                  hobbies='python',
                  record_has_been_loaded=True)

    with py_raises(werkzeug.exceptions.BadRequest):
        _api.post(payload=record)


def test_post_duplicate_id(_api):

    record = dict(id='1234',
                  e_mail='alfred@acme.com',
                  password='P455w@rd',
                  hobbies='python',
                  record_has_been_loaded=True)

    response = _api.post(payload=record)
    assert response == ('', 201, {'Location': f"/users/1234"})

    with py_raises(werkzeug.exceptions.Conflict):
        _api.post(payload=record)


def test_post_duplicate_e_mail(_api):

    record = dict(e_mail='alfred@acme.com',
                  password='P455w@rd',
                  hobbies='python',
                  record_has_been_loaded=True)

    response = _api.post(payload=record)
    assert response == ('', 201, {'Location': f"/users/alfred@acme.com"})

    with py_raises(werkzeug.exceptions.Conflict):
        _api.post(payload=record)


def test_put_malformed_request(_api):

    record = dict(password='P455w@rd',
                  hobbies='python',
                  record_has_been_loaded=True)

    with py_raises(werkzeug.exceptions.BadRequest):
        _api.put(id=None, payload=record)

    with py_raises(werkzeug.exceptions.NotFound):
        _api.put(id='*alien*', payload=record)


def test_delete_malformed_request(_api):

    with py_raises(werkzeug.exceptions.BadRequest):
        _api.delete(id=None)

    with py_raises(werkzeug.exceptions.NotFound):
        _api.delete(id='*alien*')


def test_record_life_cycle(_api):

    e_mail = 'alfred@acme.com'

    with py_raises(werkzeug.exceptions.Forbidden):  # post unknown persona
        _api.post(payload=dict(e_mail=e_mail,
                               password='P455w@rd',
                               persona='*alien*'), persona='leader')

    initial_record = dict(e_mail=e_mail,
                          password='P455w@rd',
                          hobbies='python',
                          record_has_been_loaded=True)

    response = _api.post(payload=initial_record)
    assert response == ('', 201, {'Location': f"/users/{e_mail}"})

    with py_raises(werkzeug.exceptions.Forbidden):  # put unknown persona
        _api.put(id=e_mail, payload=dict(persona='*alien*'), persona='leader')

    response = _api.login(payload=dict(id=e_mail, password='P455w@rd', hash_password=False))
    assert response.status_code == 200
    payload = json.loads(response.get_data().decode())
    print(payload)
    assert len(payload.get('bearer', '')) > 5

    response = _api.get(id=e_mail, persona='leader')
    assert response.status_code == 200
    payload = json.loads(response.get_data().decode())
    record = payload['user']
    assert record['id'] == e_mail
    for key in initial_record.keys():
        if key not in ['record_has_been_loaded', 'password']:
            assert record[key] == initial_record[key]

    e_mail_2 = 'alfred@corona.virus'

    updated_record = dict(e_mail=e_mail_2)

    with py_raises(werkzeug.exceptions.BadRequest):  # no id
        _api.put(id=None, payload=updated_record, persona='leader')

    response = _api.put(id=e_mail, payload=updated_record, persona='leader')
    assert response == ('', 204)

    with py_raises(werkzeug.exceptions.NotFound):  # previous record has disappeared
        _api.get(id=e_mail, persona='leader')

    response = _api.get(id=e_mail_2, persona='leader')
    assert response.status_code == 200
    payload = json.loads(response.get_data().decode())
    record = payload['user']
    print(record)
    assert record['id'] == e_mail_2
    print(updated_record)
    for key in updated_record.keys():
        assert record[key] == updated_record[key]
    for key in initial_record.keys():
        if key not in ['record_has_been_loaded', 'password']:
            assert key in record.keys()

    response = _api.delete(id=e_mail_2, persona='support')
    assert response == ('', 204)

    with py_raises(werkzeug.exceptions.NotFound):
        _api.get(id=e_mail_2, persona='member')


def test_record_maximum_size(_api):

    _api.record_maximum_size = 26

    with py_raises(werkzeug.exceptions.BadRequest):
        _api.post(payload={'first_name': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'},
                  persona='leader')

    with py_raises(werkzeug.exceptions.BadRequest):
        _api.put(id='fat',
                 payload={'first_name': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'},
                 persona='leader')


def test_index(_api):

    response = _api.index(persona='member')
    chunk = json.loads(response.data.decode())
    assert len(chunk['users']) == 0
    token = unquote(chunk['next'])
    assert token == 'EOF'

    _api.page_size = 5
    for n in range(_api.page_size * 2 + 3):
        _api.store.write(e_mail=f"toto+{n + 1}@alfa.com", persona='member', password='P455w@rd')

    response = _api.index(persona='member')
    chunk = json.loads(response.data.decode())
    assert len(chunk['users']) == _api.page_size
    token = unquote(chunk['next'])
    assert token != 'EOF'

def test_page(_api):

    pages = 4

    _api.page_size = 30
    _api.store.salt = 'hello world'
    for n in range(int(_api.page_size / 6) * (pages - 1) + 7):
        _api.store.write(e_mail=f"registered+{n + 1}@alfa.com", persona='registered')
        _api.store.write(e_mail=f"member+{n + 1}@alfa.com", persona='member', password='P455w@rd')
        _api.store.write(e_mail=f"leader+{n + 1}@alfa.com", persona='leader', password='P455w@rd')
        _api.store.write(e_mail=f"support+{n + 1}@alfa.com", persona='support', password='P455w@rd')
        _api.store.write(e_mail=f"robot+{n + 1}@alfa.com", persona='robot', password='P455w@rd')
        _api.store.write(e_mail=f"audit+{n + 1}@alfa.com", persona='audit', password='P455w@rd')

    response = _api.page(token=None, persona='member')
    users = json.loads(response.data.decode())['users']
    assert len(users) == 15  # 30 - 5 registered - 5 robot
    response = _api.page(token=None, persona='leader')
    users = json.loads(response.data.decode())['users']
    assert len(users) == 25  # 30 - 5 robot
    response = _api.page(token=None, persona='support')
    users = json.loads(response.data.decode())['users']
    assert len(users) == _api.page_size
    response = _api.page(token=None, persona='audit')
    users = json.loads(response.data.decode())['users']
    assert len(users) == 25  # 30 - 5 robot

    pages = 5  # because we added multiple records in previous loop
    token = None
    while token != 'EOF':
        response = _api.page(token=token, persona='member')
        chunk = json.loads(response.data.decode())
        token = unquote(chunk['next'])
        if token.startswith('/users/page/'):
            token = token[len('/users/page/'):]
        pages -= 1
    assert pages == 0

    with py_raises(werkzeug.exceptions.NotFound) as error:
        _api.page(token='EOF', persona='member')

    response = _api.page(token=_api.store._encode_token(-235), persona='support')
    chunk = json.loads(response.data.decode())
    print(chunk)
    assert len(chunk['users']) == _api.page_size
    token = unquote(chunk['next'])
    assert token != 'EOF'
