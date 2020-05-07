from pytest import raises as py_raises

from permissions import Permissions


def test_init():
    permissions = Permissions()
    assert permissions.count() == 0


def test_grant_and_authorize():
    permissions = Permissions(authorized_scopes=['scope'])
    assert permissions.count() == 0
    assert permissions.authorize(scope='scope', persona='persona', topic='topic') is False
    permissions.grant(scope='scope', persona='persona', topic='topic')
    assert permissions.count() == 1
    assert permissions.authorize(scope='scope', persona='persona', topic='topic') is True
    assert permissions.authorize(scope='*unknown*', persona='persona', topic='topic') is False
    assert permissions.authorize(scope='scope', persona='*unknown*', topic='topic') is False
    assert permissions.authorize(scope='scope', persona='persona', topic='*unknown*') is False


def test_authorized_scopes():
    permissions = Permissions()
    for scope in permissions.authorized_scopes:
        permissions.grant(scope, 'persona', 'topic')
        assert permissions.authorize(scope, 'persona', 'topic') is True
        assert permissions.authorize('*unknown*', 'persona', 'topic') is False
        assert permissions.authorize(scope, '*unknown*', 'topic') is False
        assert permissions.authorize(scope, 'persona', '*unknown*') is False


def test_grant_all():
    scopes = ['alpha', 'beta', 'gamma']
    items = [
        dict(topic='with_list', personas=['a', 'b', 'c']),
        dict(topic='with_item', persona='a'),
    ]

    permissions = Permissions(authorized_scopes=scopes)

    for scope in scopes:  # nothing is authorized
        assert permissions.authorize(scope, 'a', 'with_list') is False
        assert permissions.authorize(scope, 'b', 'with_list') is False
        assert permissions.authorize(scope, 'c', 'with_list') is False
        assert permissions.authorize(scope, 'x', 'with_list') is False
        assert permissions.authorize(scope, 'a', 'with_item') is False
        assert permissions.authorize(scope, 'x', 'with_item') is False

    for scope in scopes:  # set permissions
        permissions.grant_all(scope, items)

    for scope in scopes:  # some actions are authorized
        assert permissions.authorize(scope, 'a', 'with_list') is True
        assert permissions.authorize(scope, 'b', 'with_list') is True
        assert permissions.authorize(scope, 'c', 'with_list') is True
        assert permissions.authorize(scope, 'x', 'with_list') is False
        assert permissions.authorize(scope, 'a', 'with_item') is True
        assert permissions.authorize(scope, 'x', 'with_item') is False

    with py_raises(ValueError) as error:
        permissions.grant_all(scope='*alien*', items=items)


def test_load_file():
    store = Permissions()
    store.load(open('fixtures/permissions.yaml', 'r'))

    assert store.authorize('access-content', 'x', 'universe') is False
    assert store.authorize('access-content', 'x', 'community') is False
    assert store.authorize('access-content', 'x', 'board') is False
    assert store.authorize('access-content', 'leader', 'universe') is True
    assert store.authorize('access-content', 'leader', 'community') is True
    assert store.authorize('access-content', 'leader', 'board') is True

    assert store.authorize('manage-content', 'member', 'universe') is False
    assert store.authorize('manage-content', 'member', 'community') is False
    assert store.authorize('manage-content', 'member', 'board') is False
    assert store.authorize('manage-content', 'leader', 'universe') is True
    assert store.authorize('manage-content', 'leader', 'community') is True
    assert store.authorize('manage-content', 'leader', 'board') is True

    assert store.authorize('manage-identities', 'leader', 'member') is False
    assert store.authorize('manage-identities', 'leader', 'leader') is False
    assert store.authorize('manage-identities', 'leader', 'support') is False
    assert store.authorize('manage-identities', 'leader', 'robot') is False
    assert store.authorize('manage-identities', 'support', 'member') is True
    assert store.authorize('manage-identities', 'support', 'leader') is True
    assert store.authorize('manage-identities', 'support', 'support') is False
    assert store.authorize('manage-identities', 'support', 'robot') is True

    assert store.authorize('manage-identities', 'leader', 'update-any-to-registered') is True
    assert store.authorize('manage-identities', 'leader', 'update-any-to-leader') is True
    assert store.authorize('manage-identities', 'leader', 'update-any-to-support') is False
    assert store.authorize('manage-identities', 'leader', 'update-any- to-robot') is False
