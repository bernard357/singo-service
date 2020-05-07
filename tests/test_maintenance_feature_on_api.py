import base64
from flask import Flask
import json
from pytest import fixture, mark
from pytest_bdd import scenarios, given, when, then, parsers
from yaml import safe_load, dump

from api import app, identities, channels
from records import Records
from users import Users

scenarios('../features/maintenance.feature')


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


@given("a set of external files representing a state of the system")
def set_source_files(_context, _api):
    channels['universe'].store = Records()


@given("a system in a given state")
def set_source_system(_context, _api):
    channels['universe'].store = Records()
    # path='fixtures/sample_content.yaml')


@when(parsers.parse("the user authenticates as persona '{persona}'"))
@when(parsers.parse("the robot has been authenticated as persona '{persona}'"))
def set_persona(_context, _api, persona):
    name = 'Alfred'
    password = 'P455w@rd'
    identities.store.write(id=name, password=password, persona=persona, e_mail='P455w@rd')
    response = _api.post('/login',
                         json=dict(id=name, password=password),
                         content_type='application/json')
    assert response.status_code == 200
    payload = json.loads(response.get_data().decode())
    _context.bearer = payload.get('bearer', None)


@then("the agent can load external files into the system")
def restore_is_authorized(_context, _api):
    with open('fixtures/sample_content.yaml', "rb") as handle:
        content = handle.read()
        print(f"read {len(content)} characters from file")
        blob = base64.b64encode(content).decode()
        print(f"turned to a blob of {len(blob)} characters")
        _api.environ_base['HTTP_X_BEARER'] = _context.bearer
        response = _api.post('/restore',
                             json=dict(blob=blob),
                             content_type='application/json')
        assert response.status_code == 204


@then("the agent is prevented to load external files into the system")
def restore_is_forbidden(_context, _api):
    with open('fixtures/sample_content.yaml', "rb") as handle:
        content = handle.read()
        print(f"read {len(content)} characters from file")
        blob = base64.b64encode(content).decode()
        print(f"turned to a blob of {len(blob)} characters")
        _api.environ_base['HTTP_X_BEARER'] = _context.bearer
        response = _api.post('/restore',
                             json=dict(blob=blob),
                             content_type='application/json')
        assert response.status_code != 204


@then("the agent can dump system state to external files")
def snapshot_is_authorized(_context, _api):
    _api.environ_base['HTTP_X_BEARER'] = _context.bearer
    response = _api.get('/snapshot')
    assert response.status_code == 200
    payload = json.loads(response.get_data().decode())
    content = safe_load(base64.b64decode(payload['blob']).decode())
    assert 'users' in content.keys()
    assert 'channels' in content.keys()
    assert 'universe' in content['channels'].keys()
    assert 'community' in content['channels'].keys()
    assert 'board' in content['channels'].keys()


@then("the agent is prevented to dump system state to external files")
def snapshot_is_forbidden(_context, _api):
    _api.environ_base['HTTP_X_BEARER'] = _context.bearer
    response = _api.get('/snapshot')
    assert response.status_code == 403


@when(parsers.parse("the path '{path}' is requested over the web"))
def on_request(_context, path):
    print(f"requesting {path}")
    _context.path = path


@then(parsers.parse("system responds with message '{message}' in JSON"))
def response_has_message(_context, _api, message):
    response = _api.get(_context.path)
    assert response.status_code == 200
    payload = json.loads(response.get_data().decode())
    assert payload['message'] == message
