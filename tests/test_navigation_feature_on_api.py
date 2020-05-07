from flask import Flask
import json
from pytest import fixture, mark
from pytest_bdd import scenarios, given, when, then, parsers
import random

from api import app, channels, identities
from records import Records
from users import Users

scenarios('../features/navigation.feature')


pytestmark = mark.api


@fixture
def _context():
    print("getting a new context")

    channel = channels['universe']
    channel.store = Records(salt='hello there')

    class Context:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    return Context(channel=channel)


@fixture
def _api():
    with app.test_client() as client:
        yield client


@given("a content of 57 pages and chunks of 12 pages")
def set_content(_context, _api, count=57, chunk_size=12):
    for n in range(count):
        _context.channel.store.write(id=f"id-{n + 1}", content=f"hello {n + 1}")
    _context.channel.page_size = chunk_size


@when("the user fetches pages with token <token>")
def get_pages(_context, _api, token):
    path = f"/page/{token}" if token != 'None' else "/"
    response = _api.get(path,
                        json=dict(bearer=''),
                        content_type='application/json')
    assert response.status_code == 200
    _context.payload = json.loads(response.get_data().decode())


@then("the user gets <count> pages and get updated token <next>")
def check_pages(_context, count, next):
    print(_context.payload)
    assert len(_context.payload['items']) == int(count)
    assert _context.payload['next'] == next


@given("a community of 36 persons and chunks of 10 records")
def set_community(_context, _api, count=36, chunk_size=10):
    identities.store = Users()
    for n in range(count):
        identities.store.write(e_mail=f"id-{n + 1}@acme.com",
                               password='P455w@rd',
                               description=f"hello {n + 1}",
                               persona=random.choice(['member', 'leader', 'audit']))
    identities.page_size = chunk_size

    name = 'Marc'
    persona = 'member'
    password = 'P455w@rd'
    identities.store.write(name, password=password, persona=persona, e_mail='marc@acme.com')
    response = _api.post('/login',
                         json=dict(id=name, password=password),
                         content_type='application/json')
    assert response.status_code == 200
    payload = json.loads(response.get_data().decode())
    print(payload)
    _context.bearer = payload.get('bearer', None)


@when("the user fetches profiles with token <token>")
def get_profiles(_context, _api, token):
    _api.environ_base['HTTP_X_BEARER'] = _context.bearer
    path = f"/users/page/{token}" if token != 'None' else "/users"
    response = _api.get(path)
    assert response.status_code == 200
    _context.payload = json.loads(response.get_data().decode())


@then("the user gets <count> profiles and get updated token <next>")
def check_profiles(_context, count, next):
    print(_context.payload)
    assert len(_context.payload['users']) == int(count)
    assert _context.payload['next'] == next
