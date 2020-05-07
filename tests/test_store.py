import datetime
from io import StringIO
from pytest import fixture, mark, raises as py_raises

from store import Store


pytestmark = mark.wip


@fixture
def _store():
    items = [dict(id="id-{}".format(n + 1),
                  side="side-{}".format(n + 1),
                  text='hello world') for n in range(5)]

    store = Store()
    for item in items:
        store.put(**item)

    return store


def test_init():
    store = Store()
    assert len(store.ids()) == 0


def test_record_life_cycle():
    id = '01234567890-c01'
    initial_record = dict(id=id, title='hello world', description='etc.')
    updated_record = dict(id=id, title='another title')

    store = Store()  # empty store
    assert store.get(id=id) is None

    store.put(**initial_record)
    record = store.get(id=id)
    assert record['title'] == initial_record['title']
    assert record['description'] == initial_record['description']

    store.put(**updated_record)
    record = store.get(id=id)
    assert record['title'] == updated_record['title']
    assert record.get('description', None) is None

    store.delete(id=id)
    assert store.get(id=id) is None


def test_delete_with_unknown_id(_store):
    _store.delete(id='*here*there*is*no*alien*yet*')


def test_list_ids(_store):

    ids = _store.ids()
    assert ids[0] == 'id-1'

    ids = _store.ids_by('side', reverse=False)
    assert ids[0] == 'id-1'

    ids = _store.ids_by('side', reverse=True)
    assert ids[0] == 'id-5'
