from flask import Flask
import json
import jwt
from pytest import fixture, mark, raises as py_raises
from pytest_bdd import scenarios, given, when, then, parsers
import werkzeug

from api import app, identities
import bearers
from users import Users

scenarios('../features/personas.feature')


pytestmark = mark.api


@fixture
def _context():
    print("getting a new context")
    identities.store = Users()

    class Context:
        pass

    return Context()


@fixture
def _api():
    with app.test_client() as client:
        yield client


@given("a surfer navigating the site")
def no_user_record(_context, _api):
    _context.proxy_bearer = ''


@given(parsers.parse("a surfer navigating the site protected by secret '{secret}'"))
def set_secret(_context, _api, secret):
    identities.store.set_bearer_secret(secret)
    _context.bearer_secret = secret


@given(parsers.parse("a user authenticated as '{name}' and as persona '{persona}'"))
def add_proxy(_context, _api, name, persona, password='P455w@rd'):
    identities.store.write(id=name, password=password, persona=persona, e_mail='a@b.c')
    response = _api.post('/login',
                         json=dict(id=name, password=password),
                         content_type='application/json')
    assert response.status_code == 200
    payload = json.loads(response.get_data().decode())
    _context.proxy_name = name
    _context.proxy_bearer = payload.get('bearer', None)


@when(parsers.parse("surfer '{name}' registers with password '{password}'"))
def self_registrant(_context, _api, name, password):
    e_mail = None if name == '-' else 'a@b.c'
    response = _api.post('/register',
                         json=dict(id=name, e_mail=e_mail, password=password),
                         content_type='application/json')
    assert response.status_code in [201, 400]
    _context.status_code = response.status_code


@when(parsers.parse("surfer '{name}' registers with secret '{secret}' and password '{password}'"))
def self_support(_context, _api, name, secret, password):
    assert _context.bearer_secret == secret
    identities.store.set_bearer_secret(_context.bearer_secret)
    response = _api.post('/register',
                         json=dict(id=name, e_mail='a@b.c', secret=secret, password=password),
                         content_type='application/json')
    assert response.status_code == 201


@when(parsers.parse("user '{support}' registers identity '{name}' with password '{password}' and persona '{persona}'"))
def add_registrant(_context, _api, support, name, password, persona):
    assert _context.proxy_name == support
    _api.environ_base['HTTP_X_BEARER'] = _context.proxy_bearer
    response = _api.post('/register',
                         json=dict(id=name, e_mail='a@b.c', persona=persona, password=password),
                         content_type='application/json')
    _context.status_code = response.status_code


@when(parsers.parse("user '{promoter}' promotes '{name}' to '{persona}'"))
def promote_registrant(_context, _api, promoter, name, persona):
    assert _context.proxy_name == promoter
    _api.environ_base['HTTP_X_BEARER'] = _context.proxy_bearer
    response = _api.put(f"/users/{name}",
                        json=dict(id=name, persona=persona),
                        content_type='application/json')
    _context.status_code = response.status_code


@when(parsers.parse("user '{support}' modifies profile of '{name}' with password '{password}'"))
def modify_profile(_context, _api, support, name, password):
    assert _context.proxy_name == support
    _api.environ_base['HTTP_X_BEARER'] = _context.proxy_bearer
    response = _api.put(f"/users/{name}",
                        json=dict(id=name, password=password),
                        content_type='application/json')
    _context.status_code = response.status_code


@when(parsers.parse("user '{support}' deletes profile of '{name}'"))
def delete_profile(_context, _api, support, name, password):
    assert _context.proxy_name == support
    _api.environ_base['HTTP_X_BEARER'] = _context.proxy_bearer
    response = _api.delete(f"/users/{name}")
    _context.status_code = response.status_code


@then("the operation is denied")
def deny_operation(_context):
    assert _context.status_code in [400, 403]


@then(parsers.parse("surfer '{name}' has persona '{persona}'"))
def check_persona(_context, _api, name, persona):
    record = identities.store.read(id=name)
    assert record['id'] == name
    assert record['persona'] == persona


@then(parsers.parse("surfer '{name}' does NOT have persona '{persona}'"))
def persona_has_not_been_modified(_context, _api, name, persona):
    record = identities.store.read(id=name)
    assert record['id'] == name
    assert record['persona'] != persona
