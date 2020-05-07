from flask import Flask
import json
import jwt
from pytest import fixture, mark, raises as py_raises
from pytest_bdd import scenarios, given, when, then, parsers
import werkzeug

from api import app, identities
import bearers
from users import Users

scenarios('../features/authentication.feature')


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


@given("a user record has identity <identity> and password <password> and persona <persona>")
def add_user_record(_context, _api, identity, password, persona):
    identities.store.write(id=identity, password=password, persona=persona, e_mail='a@b.c')


@when("the user authenticates successfully with identity <label> and password <secret>")
def submit_password_and_authenticate(_context, _api, label, secret):
    response = _api.post('/login',
                         json=dict(id=label, password=secret),
                         content_type='application/json')
    assert response.status_code == 200
    payload = json.loads(response.get_data().decode())
    _context.bearer = payload.get('bearer', None)


@when("the user fails to authenticate with identity <label> and password <secret>")
def submit_password_and_fail(_context, _api, label, secret):
    response = _api.post('/login',
                         json=dict(id=label, password=secret),
                         content_type='application/json')
    assert response.status_code != 200
    _context.bearer = None


@when("the user authenticates successfully with identity <identity> and hash <hash> and delta <delta>")
def submit_signature_and_authenticate(_context, _api, identity, hash, delta):
    salt = bearers.get_salt()
    stamp = bearers.get_stamp(delta=int(delta)).strftime('%Y%m%dT%H%M%SZ')
    blob = bearers.compute_signature(hash=hash,
                                     salt=salt,
                                     stamp=stamp)
    response = _api.post('/signin',
                         json=dict(id=identity,
                                   signature=blob,
                                   salt=salt,
                                   stamp=stamp),
                         content_type='application/json')
    assert response.status_code == 200
    payload = json.loads(response.get_data().decode())
    _context.bearer = payload.get('bearer', None)


@when("the user fails to authenticate with identity <label> and hash <hash> and delta <delta>")
def submit_signature_and_fail(_context, _api, label, hash, delta):
    salt = bearers.get_salt()
    stamp = bearers.get_stamp(delta=int(delta)).strftime('%Y%m%dT%H%M%SZ')
    blob = bearers.compute_signature(hash=hash,
                                     salt=salt,
                                     stamp=stamp)
    response = _api.post('/signin',
                         json=dict(id=label,
                                   signature=blob,
                                   salt=salt,
                                   stamp=stamp),
                         content_type='application/json')
    assert response.status_code != 200
    _context.bearer = None


@then("there is no valid bearer")
def bearer_is_absent(_context):
    assert _context.bearer is None


@then("the bearer is for identity <identity> and persona <persona>")
def bearer_is_present(_context, _api, identity, persona):
    response = _api.post('/check',
                         json=dict(bearer=_context.bearer),
                         content_type='application/json')
    assert response.status_code == 200
    payload = json.loads(response.get_data().decode())
    assert payload['identity'] == identity
    assert payload['persona'] == persona


@given("a secret '5b49d1280e8517e54daeeb90034334ae' and validity of 60 minutes and expiration after 720 minutes")
def set_bearer_context(_context, _api):
    print("setting bearer context")
    identities.store.set_bearer_secret('5b49d1280e8517e54daeeb90034334ae')
    identities.store.bearer_validity = 60
    identities.store.bearer_expiration = 720


@when("a bearer is submitted with identity <identity> and secret <secret> and delta <delta>")
def set_submitted_bearer(_context, identity, secret, delta):
    stamp = bearers.get_stamp(delta=int(delta)).strftime('%Y%m%dT%H%M%SZ')
    _context.bearer = bearers.encode_bearer(identity=identity, secret=secret, persona='persona', stamp=stamp)


@when("the submitted bearer is renewed")
def set_renewed_bearer(_context, _api):
    try:
        response = _api.post('/renew',
                             json=dict(bearer=_context.bearer),
                             content_type='application/json')
        assert response.status_code == 200
        payload = json.loads(response.get_data().decode())
        _context.bearer = payload.get('bearer', None)
    except:
        print("bearer could not be renewed")
        _context.bearer = None


@then("the submitted bearer is for <label> and is <valid> and <renewable>")
def submitted_bearer_is_checked(_context, _api, label, valid='Yes', renewable='Yes'):
    response = _api.post('/check',
                         json=dict(bearer=_context.bearer),
                         content_type='application/json')
    if label == '-':
        assert response.status_code != 200

    else:
        assert response.status_code == 200
        payload = json.loads(response.get_data().decode())
        assert payload['identity'] == label
        assert payload['is_valid'] == (valid == 'Yes')
        assert payload['is_renewable'] == (renewable == 'Yes')


@then("the renewed bearer is for <identity> and is valid and renewable")
def renewed_bearer_is_checked(_context, _api, identity):
    response = _api.post('/check',
                         json=dict(bearer=_context.bearer),
                         content_type='application/json')
    assert response.status_code == 200
    payload = json.loads(response.get_data().decode())
    assert payload['identity'] == identity
    assert payload['persona'] == 'persona'
