from flask import Flask
import json
import jwt
from pytest import fixture, mark, raises as py_raises
from pytest_bdd import scenarios, given, when, then, parsers
import werkzeug

from api import app, identities
import bearers
from users import Users

scenarios('../features/authorization.feature')


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


@given("a user authenticated as <name> and as persona <persona>")
def add_user_record(_context, _api, name, persona, password='P455w@rd'):
    identities.store.write(id=name, password=password, persona=persona, e_mail=f"{name}@acme.com")
    response = _api.post('/login',
                         json=dict(id=name, password=password),
                         content_type='application/json')
    assert response.status_code == 200
    payload = json.loads(response.get_data().decode())
    print(payload)
    _context.bearer = payload.get('bearer', None)
    _api.environ_base['HTTP_X_BEARER'] = _context.bearer


@when("the user <name> visits the channel <channel>")
def visit_channel_index(_context, _api, name, channel):
    routes = dict(community='/community/', board='/board/')
    response = _api.get(routes.get(channel, '/'))
    _context.status_code = response.status_code


@then("the user <name> is given access to the channel <channel>")
def allow_access_to_channel(_context, name, channel):
    assert _context.status_code == 200


@then("access to the channel <channel> is denied to <name>")
def deny_access_to_channel(_context, name, channel):
    assert _context.status_code == 403


@when("the user <name> visits the community index")
def visit_community_index(_context, _api, name):
    response = _api.get('/users')
    _context.status_code = response.status_code


@then("the user <name> can list profiles")
def allow_list_of_profiles(_context, name):
    assert _context.status_code == 200


@then("list of profiles is denied to <name>")
def deny_list_of_profiles(_context, name):
    assert _context.status_code == 403
