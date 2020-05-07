import datetime
from io import StringIO
import jwt
from pytest import fixture, raises as py_raises

import bearers
from users import Users, AUTHORIZED_PERSONAS


def test_init():
    store = Users()
    assert store.count() == 0
    assert store.authorized_personas == AUTHORIZED_PERSONAS


def test_record_life_cycle():

    id = '01234567890'
    initial_record = dict(id=id, persona='member', password='P4SSw@rd', e_mail='a@b.c')
    updated_record = dict(id=id, password='anotherOne')

    store = Users()
    assert store.read(id=id) is None

    store.write(**initial_record)
    record = store.read(id=id)
    for key in initial_record.keys():
        if key == 'password':
            assert record[key] == '7b22184aa8082c76e63391e179c66644'
        else:
            assert record[key] == initial_record[key]

    store.write(**updated_record)  # change password
    record = store.read(id=id)
    for key in updated_record.keys():
        if key == 'password':
            assert record[key] == '5b8892d5956d6870679b048cd982583c'
        else:
            assert record[key] == updated_record[key]
    for key in initial_record.keys():
        assert key in record.keys()

    store.delete(id=id)
    assert store.read(id=id) is None


def test_write_password_with_no_hash():

    store = Users()
    store.write(id='id', persona='member', password='PA55w@rd', e_mail='a@b.c', record_has_been_loaded=True)
    record = store.read(id='id')
    assert record['password'] == 'PA55w@rd'

    store.write(id='id', password='another', record_has_been_loaded=True)
    record = store.read(id='id')
    assert record['password'] == 'another'


def test_write_with_wrong_persona():

    store = Users()
    with py_raises(ValueError) as error:
        store.write(id='id', persona='*alien*', password='123', e_mail='a@b.c')


def test_write_without_id():

    store = Users()
    assert store.write(id=None, persona='member', password='456', e_mail='a@b.c') == 'a@b.c'


def test_delete_with_unknown_id():

    store = Users()
    store.write(id='01234567890', persona='member', password='123', e_mail='a@b.c')
    store.delete(id='*aliens*are*everywhere*')


def test_authenticate_signature():

    db = Users()
    db.write(id='Alice', password='P455w@rd', persona='support', e_mail='a@b.c')

    salt = 'salt'
    stamp = bearers.get_current_stamp()

    # unknown user
    with py_raises(ValueError) as error:
        db.authenticate_signature('Bob',
                                  signature='*signature',
                                  salt=salt,
                                  stamp=stamp)

    # really need salted call
    with py_raises(TypeError) as error:
        db.authenticate_signature('Alice',
                                  signature='*signature',
                                  stamp=stamp)

    # really need stamp
    with py_raises(TypeError) as error:
        db.authenticate_signature('Alice',
                                  signature='*signature',
                                  salt=salt)

    # random credentials does not pass
    with py_raises(ValueError) as error:
        db.authenticate_signature('Alice',
                                  signature='*signature',
                                  salt=salt,
                                  stamp=stamp)

    # password hash does not work, there is a need for real signature
    with py_raises(ValueError) as error:
        db.authenticate_signature('Alice',
                                  signature='5b49d1280e8517e54daeeb90034334ae',
                                  salt=salt,
                                  stamp=stamp)

    # incorrect salt in signature computation
    blob = bearers.compute_signature(hash='5b49d1280e8517e54daeeb90034334ae',
                                     salt='1234',
                                     stamp=stamp)
    with py_raises(ValueError) as error:
        db.authenticate_signature('Alice',
                                  signature=blob,
                                  salt=salt,
                                  stamp=stamp)

    # compute correct signature and check it
    blob = bearers.compute_signature(hash='5b49d1280e8517e54daeeb90034334ae',
                                     salt=salt,
                                     stamp=stamp)
    bearer = db.authenticate_signature('Alice',
                                       signature=blob,
                                       salt=salt,
                                       stamp=stamp)

    assert bearers.decode_bearer(secret=None, bearer=bearer).persona == 'support'
