import datetime
from flask import Flask
import io
import json
import jwt
import hashlib
import logging
from pytest import fixture, mark, raises as py_raises
from urllib.parse import unquote
import werkzeug

from api_channel import Channel
from api_identities import Identities
from commands import Commands


# pytestmark = mark.wip


memory_stream = io.StringIO()
commands = Commands(stream=memory_stream)

app = Flask(__name__)
identities = Identities(emitter=commands.emit)
identities.register_routes(app)
identities.store.write(id='Sylvia', password='P455w@rd', persona='support', e_mail='a@b.c')
channel = Channel(name='board', emitter=commands.emit)
channel.register_routes(app, wrapper=identities.inject_identity)


@fixture
def _api():
    with app.test_client() as client:
        yield client


item_id = '01234567890-c01'
item_initial = dict(id=item_id, title='hello world', description='etc.')
item_version2 = dict(id=item_id, title='another title')
item_version3 = dict(id=item_id, description='an updated description')
item_version4 = dict(id=item_id, status='brand new status')
item_final = dict(id=item_id,
                  title='another title',
                  description='an updated description',
                  status='brand new status')


user_id = 'Alfred'
user_initial = dict(id=user_id, e_mail='alfred@acme.com', label='Alfred Gontran des Hauts de France', description='etc.')
user_version2 = dict(id=user_id, label='Alfred Bourgeois')
user_version3 = dict(id=user_id, description='survivor of the French Revolution')
user_version4 = dict(id=user_id, eye_color='brown')
user_final = dict(id=user_id,
                  label='Alfred Bourgeois',
                  description='survivor of the French Revolution',
                  eye_color='brown')


class Dispatcher:

    def __init__(self):
        self.count = 0
        self.hash = ''

    def process(self, persona, scope, action, payload, **kwargs):
        assert scope in ['channel:board', 'identities']
        assert action in ['post', 'put', 'delete']
        assert payload.get('id') is not None
        self.count += 1
        message = self.hash + scope + action + json.dumps(payload)
        self.hash = hashlib.md5(message.encode('utf-8')).hexdigest()


@mark.dependency()
def test_emit_from_channel(_api):

    assert channel.store.count() == 0

    response = _api.post('/login',
                         json=dict(id='Sylvia', password='P455w@rd'),
                         content_type='application/json')
    assert response.status_code == 200
    payload = json.loads(response.get_data().decode())
    bearer = payload.get('bearer', None)

    response = _api.post('/check',
                         json=dict(bearer=bearer),
                         content_type='application/json')
    assert response.status_code == 200
    payload = json.loads(response.get_data().decode())

    response = _api.post('/board/',
                         json=dict(bearer=bearer, **item_initial),
                         content_type='application/json')
    assert response.status_code == 201
    response = _api.delete(f'/board/{item_id}',
                           json=dict(bearer=bearer),
                           content_type='application/json')
    assert response.status_code == 204
    response = _api.post('/board/',
                         json=dict(bearer=bearer, **item_initial),
                         content_type='application/json')
    assert response.status_code == 201
    response = _api.put(f'/board/{item_id}',
                        json=dict(bearer=bearer, **item_version2),
                        content_type='application/json')
    assert response.status_code == 204
    response = _api.put(f'/board/{item_id}',
                        json=dict(bearer=bearer, **item_version3),
                        content_type='application/json')
    assert response.status_code == 204
    response = _api.put(f'/board/{item_id}',
                        json=dict(bearer=bearer, **item_version4),
                        content_type='application/json')
    assert response.status_code == 204

    dispatcher = Dispatcher()
    commands.parse(dispatchers=[dispatcher.process])
    assert dispatcher.count == 6
    assert dispatcher.hash == '5d64895115d2100a7d2a59239c11d393'


@mark.dependency(depends=['test_emit_from_channel'])
def test_emit_from_identities(_api):

    assert identities.store.count() == 1

    response = _api.post('/login',
                         json=dict(id='Sylvia', password='P455w@rd'),
                         content_type='application/json')
    assert response.status_code == 200
    payload = json.loads(response.get_data().decode())
    bearer = payload.get('bearer', None)

    response = _api.post('/register',
                         json=dict(bearer=bearer, **user_initial),
                         content_type='application/json')
    assert response.status_code == 201
    response = _api.delete(f'/users/{user_id}',
                           json=dict(bearer=bearer),
                           content_type='application/json')
    assert response.status_code == 204
    response = _api.post('/register',
                         json=dict(bearer=bearer, **user_initial),
                         content_type='application/json')
    assert response.status_code == 201
    response = _api.put(f'/users/{user_id}',
                        json=dict(bearer=bearer, **user_version2),
                        content_type='application/json')
    assert response.status_code == 204
    response = _api.put(f'/users/{user_id}',
                        json=dict(bearer=bearer, **user_version3),
                        content_type='application/json')
    assert response.status_code == 204
    response = _api.put(f'/users/{user_id}',
                        json=dict(bearer=bearer, **user_version4),
                        content_type='application/json')
    assert response.status_code == 204

    dispatcher = Dispatcher()
    commands.parse(dispatchers=[dispatcher.process])
    assert dispatcher.count == 12
    assert dispatcher.hash == 'd92bbc0b25f2741ce85aa72625703c17'


@mark.dependency(depends=['test_emit_from_identities'])
def test_dispatch_on_replay(_api):

    commands.enabled = False

    response = _api.post('/login',
                         json=dict(id='Sylvia', password='P455w@rd'),
                         content_type='application/json')
    assert response.status_code == 200
    payload = json.loads(response.get_data().decode())
    bearer = payload.get('bearer', None)

    response = _api.delete(f'/board/{item_id}',
                           json=dict(bearer=bearer),
                           content_type='application/json')
    assert response.status_code == 204

    response = _api.delete(f'/users/{user_id}',
                           json=dict(bearer=bearer),
                           content_type='application/json')
    assert response.status_code == 204

    assert channel.store.count() == 0
    assert identities.store.count() == 1

    commands.parse(dispatchers=[channel.replay, identities.replay])

    record = channel.store.read(id=item_id)
    assert record['id'] == item_id
    for key in item_final.keys():
        assert record[key] == item_final[key]

    record = identities.store.read(id=user_id)
    assert record['id'] == user_id
    for key in user_final.keys():
        assert record[key] == user_final[key]


def test_init():
    commands = Commands(path='fixtures/commands.yaml')


replay_string = '''
---
action: post
payload:
  id: Robot
  password: P455w@rd
  email: robot@acme.com
  persona: robot
persona: support
scope: identities
stamp: 1588105424.7650208
---
action: post
payload:
  id: Robot
  password: P455w@rd
  email: robot@acme.com
  persona: robot
persona: support
scope: identities
stamp: 1088105420.00  # before previous record
---
action: post
payload:
  foo: bar
  id: leader board
persona: leader
scope: channel:board
stamp: 1588105424.0876758
---
action: post
payload:
  foo: bar
  id: leader board
persona: leader
scope: channel:board
stamp: 1088105420.00  # before previous record

'''


def test_replay_with_stamp():
    replay_stream = io.StringIO(replay_string)
    commands = Commands(stream=replay_stream)
    commands.parse(dispatchers=[channel.replay, identities.replay])
