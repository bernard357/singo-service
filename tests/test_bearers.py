import datetime
import jwt
from pytest import fixture, mark, raises as py_raises

import bearers


def test_get_salt():
    assert bearers.get_salt() is not None
    assert len(bearers.get_salt()) > 16


def test_get_current_stamp():
    assert len(bearers.get_current_stamp()) == 16


def test_stamp_is_valid():
    expired = (datetime.datetime.utcnow() - datetime.timedelta(minutes=15)).strftime('%Y%m%dT%H%M%SZ')
    assert bearers.stamp_is_valid(expired, validity=5) is False

    futuristic = (datetime.datetime.utcnow() + datetime.timedelta(minutes=15)).strftime('%Y%m%dT%H%M%SZ')
    assert bearers.stamp_is_valid(futuristic) is False

    correct = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    assert bearers.stamp_is_valid(correct) is True


def test_encode_bearer():
    secret = 'secret'

    payload = dict(identity='1234',
                   persona='persona',
                   label='Alice (ACME)',
                   e_mail='alice@acme.com')

    encoded = bearers.encode_bearer(secret, **payload)
    assert len(encoded) > 7

    decoded = bearers.decode_bearer(secret=secret, bearer=encoded)
    assert decoded.identity == '1234'
    assert decoded.persona == 'persona'
    assert decoded.label == 'Alice (ACME)'
    assert decoded.e_mail == 'alice@acme.com'
    assert len(decoded.salt) > 7
    assert len(decoded.stamp) > 7
    assert decoded.is_valid == True
    assert decoded.is_renewable == True


def test_decode_bearer():
    secret = 'secret'

    # missing stamp in bearer
    payload = dict(identity='Alice',
                   persona='persona',
                   salt='salt')
    bearer = jwt.encode(payload, secret, algorithm='HS256').decode()
    with py_raises(ValueError) as error:
        bearers.decode_bearer(secret=secret, bearer=bearer)

    # missing salt in bearer
    payload = dict(identity='Alice',
                   persona='persona',
                   stamp='stamp')
    bearer = jwt.encode(payload, secret, algorithm='HS256').decode()
    with py_raises(ValueError) as error:
        bearers.decode_bearer(secret=secret, bearer=bearer)


def test_compute_signature():
    hash = '12345'
    salt = '67890'
    stamp = datetime.datetime(2017, 6, 21, 18, 25, 30).strftime('%Y%m%dT%H%M%SZ')
    assert bearers.compute_signature(hash=hash, salt=salt, stamp=stamp) == '1559c8c19d4eeac05cd0c61c42465a19901643f767a505d5289692613de6fee6'
