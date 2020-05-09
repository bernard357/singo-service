from flask import Flask
import json
from pytest import fixture, mark
from pytest_bdd import scenarios, given, when, then, parsers

from api import app, identities, maintenance
from users import Users

scenarios('../features/creation.feature')


pytestmark = mark.api


@fixture
def _context():
    print("getting a new context")
    with open('fixtures/test_state.yaml', 'r') as stream:
        maintenance.import_content(stream)
    identities.store = Users()

    class Context:
        pass

    return Context()


@fixture
def _api():
    with app.test_client() as client:
        yield client


@given("a user authenticated as <name> and as persona <persona>")
def add_user(_context, _api, name, persona, password='P455w@rd'):
    identities.store.write(id=name, password=password, persona=persona, e_mail=f"{name}@acme.com")
    response = _api.post('/login',
                         json=dict(id=name, password=password),
                         content_type='application/json')
    assert response.status_code == 200
    payload = json.loads(response.get_data().decode())
    print(payload)
    _context.bearer = payload.get('bearer', None)
    _api.environ_base['HTTP_X_BEARER'] = _context.bearer


@when("the user <name> adds a page <title> to path <path>")
def add_page(_context, _api, name, title, path):
    response = _api.post(path,
                         json=dict(id=title, foo='bar'),
                         content_type='application/json')
    _context.status_code = response.status_code


@then("page <title> is listed first at path <path>")
def check_first_page(_context, _api, title, path):
    assert _context.status_code == 201
    index = path[:-1] if len(path) > 1 else path  # remove trailing slash
    response = _api.get(path)
    assert response.status_code == 200
    payload = json.loads(response.get_data().decode())
    print(payload['items'])
    for item in payload['items']:
        print(item['id'])
    first = payload['items'][0]
    print(first)
    assert first['id'] == title
    assert payload['next'] == 'EOF'


@then("an error code is returned")
def check_error_code(_context):
    assert _context.status_code != 200
