from flask import Flask
import json
import jwt
from pytest import fixture, mark, raises as py_raises
from pytest_bdd import scenarios, given, when, then, parsers
import werkzeug

from api import app, identities
import bearers
from users import Users

scenarios('../features/profiles.feature')


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


@given(parsers.parse("a surfer registered with e-mail '{address}' and password '{password}' and persona '{persona}'"))
def given_surfer_with_persona(address, password, persona, _context, _api):
    identities.store.write(e_mail=address, password=password, persona=persona)


@given("a person registered with identity <identity> and persona <persona>")
def given_identity_with_persona(identity, persona, _context, _api):
    identities.store.write(e_mail=identity, password='P455w@rd', persona=persona)


@when("a surfer registered as <actor> and <role>")
def given_actor_with_role(actor, role, _context, _api):
    identities.store.write(e_mail=actor, password='P455w@rd', persona=role)


@when(parsers.parse("surfer has been authenticated with '{address}' and password '{password}'"))
def authenticate_surfer_credentials(address, password, _context, _api):
    response = _api.post('/login',
                         json=dict(id=address, password=password),
                         content_type='application/json')
    assert response.status_code == 200
    payload = json.loads(response.get_data().decode())
    _context.bearer = payload.get('bearer', None)
    _api.environ_base['HTTP_X_BEARER'] = _context.bearer


@when("surfer has been authenticated as <actor>")
def authenticate_actor_credentials(actor, _context, _api):
    response = _api.post('/login',
                         json=dict(id=actor, password='P455w@rd'),
                         content_type='application/json')
    assert response.status_code == 200
    payload = json.loads(response.get_data().decode())
    _context.bearer = payload.get('bearer', None)
    _api.environ_base['HTTP_X_BEARER'] = _context.bearer


@then(parsers.parse("surfer can read the index of profiles"))
def surfer_can_read_index_of_profiles(_context, _api):
    response = _api.get('/users')
    assert response.status_code == 200
    response = _api.get('/users/page/*alien*')
    assert response.status_code == 404


@then(parsers.parse("surfer is prevented to read the index of profiles"))
def surfer_is_prevented_to_read_index_of_profiles(_context, _api):
    response = _api.get('/users')
    assert response.status_code == 403
    response = _api.get('/users/page/*alien*')
    assert response.status_code == 403


@then(parsers.parse("surfer can read profile of '{address}'"))
def surfer_can_read_profile_of(address, _context, _api):
    response = _api.get(f"/users/{address}")
    assert response.status_code == 200


@then("surfer can read profile of <identity>")
def actor_can_read_profile_of(identity, _context, _api):
    response = _api.get(f"/users/{identity}")
    assert response.status_code == 200


@then(parsers.parse("surfer is prevented to read profile of '{address}'"))
def surfer_is_prevented_to_read_profile_of(address, _context, _api):
    response = _api.get(f"/users/{address}")
    assert response.status_code == 403


@then("surfer is prevented to read profile of <identity>")
def actor_is_prevented_to_read_profile_of(identity, _context, _api):
    response = _api.get(f"/users/{identity}")
    assert response.status_code == 403


@then(parsers.parse("surfer can modify profile of '{address}'"))
def surfer_can_modify_profile_of(address, _context, _api):
    response = _api.put(f"/users/{address}",
                        json=dict(content='<p>hello world</p>'),
                        content_type='application/json')
    assert response.status_code == 204


@then("surfer can modify profile of <identity>")
def actor_can_modify_profile_of(identity, _context, _api):
    response = _api.put(f"/users/{identity}",
                        json=dict(content='<p>hello world</p>'),
                        content_type='application/json')
    assert response.status_code == 204


@then(parsers.parse("surfer is prevented to modify profile of '{address}'"))
def surfer_is_prevented_to_modify_profile_of(address, _context, _api):
    response = _api.put(f"/users/{address}",
                        json=dict(content='<p>hello world</p>'),
                        content_type='application/json')
    assert response.status_code == 403


@then("surfer is prevented to modify profile of <identity>")
def actor_is_prevented_to_modify_profile_of(identity, _context, _api):
    response = _api.put(f"/users/{identity}",
                        json=dict(content='<p>hello world</p>'),
                        content_type='application/json')
    assert response.status_code == 403


@then(parsers.parse("surfer can delete profile of '{address}'"))
def surfer_can_delete_profile_of(address, _context, _api):
    response = _api.delete(f"/users/{address}")
    assert response.status_code == 204


@then("surfer can delete profile of <identity>")
def actor_can_delete_profile_of(identity, _context, _api):
    response = _api.delete(f"/users/{identity}")
    assert response.status_code == 204


@then(parsers.parse("surfer is prevented to delete profile of '{address}'"))
def surfer_is_prevented_to_delete_profile_of(address, _context, _api):
    response = _api.delete(f"/users/{address}")
    assert response.status_code == 403


@then("surfer is prevented to delete profile of <identity>")
def actor_is_prevented_to_delete_profile_of(identity, _context, _api):
    response = _api.delete(f"/users/{identity}")
    assert response.status_code == 403
