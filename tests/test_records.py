import datetime
from io import StringIO
from pytest import fixture, mark, raises as py_raises

from records import Records


@fixture
def _records():
    items = [dict(id="id-{}".format(n + 1), text='hello world') for n in range(5)]

    records = Records()
    for item in items:
        records.write(**item)

    return records


def test_init():
    store = Records()
    assert store.count() == 0


def test_record_life_cycle():
    id = '01234567890-c01'
    initial_record = dict(id=id, title='hello world', description='etc.')
    updated_record = dict(id=id, title='another title')

    store = Records()  # empty store
    assert store.read(id=id) is None

    assert id == store.write(**initial_record)
    record = store.read(id=id)
    for key in initial_record.keys():
        assert record[key] == initial_record[key]

    store.write(**updated_record)  # update some field
    record = store.read(id=id)
    for key in updated_record.keys():
        assert record[key] == updated_record[key]
    for key in initial_record.keys():
        assert key in record.keys()

    store.delete(id=id)  # delete the record
    assert store.read(id=id) is None


def test_write_on_same_id():
    store = Records()
    id = store.write(title='hello world')
    store.write(id=id, title='another title')


def test_write_on_new_id(_records):
    id = '*aliens*are*everywhere*'
    assert _records.write(id=id, title='another title') == id


def test_delete_with_unknown_id(_records):
    _records.delete(id='*here*there*is*no*alien*yet*')


def test_chunk_is_ordered_correctly(_records):
    chunk = _records.chunk(token=None)
    assert chunk.count == 5
    assert chunk.token == 'EOF'
    assert chunk.records[0]['id'] == 'id-5'
    assert chunk.records[1]['id'] == 'id-4'
    assert chunk.records[2]['id'] == 'id-3'
    assert chunk.records[3]['id'] == 'id-2'
    assert chunk.records[4]['id'] == 'id-1'


def test_chunk_chaining_with_token():
    records = Records(salt='hello world')
    for n in range(36):
        records.write(id=f"id-{n + 1}", content=f"hello {n + 1}")

    chunk = records.chunk(token=None)
    assert chunk.count == 10
    assert chunk.token == 'aGVsbG8gd29ybGQxMA=='

    chunk = records.chunk(token=records._encode_token(-235))
    assert chunk.count == 10
    assert chunk.token == 'aGVsbG8gd29ybGQxMA=='

    with py_raises(ValueError) as error:
        chunk = records.chunk(token='EOF')

    chunk = records.chunk(token=records._encode_token(235))
    assert chunk.count == 0
    assert chunk.token == 'EOF'

    with py_raises(ValueError) as error:
        chunk = records.chunk(token='azerty')

    with py_raises(ValueError) as error:
        chunk = records.chunk(token='12345')


def test_scan(_records):
    count = 0
    for item in _records.scan():
        count += 1
    assert count == 5
