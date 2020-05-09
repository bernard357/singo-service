import copy
from flask import jsonify, request, abort, url_for, make_response
from functools import wraps
import jwt
import logging
from sys import getsizeof

from permissions import Permissions
from users import Users, NotFoundError


logger = logging.getLogger(__name__)


class Identities:

    def __init__(self, permissions=None, store=None, emitter=None):
        self.secret_attributes = ['password']
        self.permissions = permissions or Permissions(path='fixtures/permissions.yaml')
        self.store = store or Users()
        self.emitter = emitter
        self.replay_stamp = None
        self.page_size = 10
        self.record_maximum_size = 100000
        self.routes = []
        self._add_url_rule('/login', 'login', self.login, methods=['POST'])
        self._add_url_rule('/signin', 'signin', self.signin, methods=['POST'])
        self._add_url_rule('/check', 'check', self.check_bearer, methods=['GET', 'POST'])
        self._add_url_rule('/renew', 'renew', self.renew_bearer, methods=['GET', 'POST'])
        self._add_url_rule('/users', 'index', self.index)
        self._add_url_rule('/users/page/<token>', 'page', self.page)
        self._add_url_rule('/register', 'post', self.post, methods=['POST'])
        self._add_url_rule('/users/<id>', 'get', self.get)
        self._add_url_rule('/users/<id>', 'put', self.put, methods=['PUT'])
        self._add_url_rule('/users/<id>', 'delete', self.delete, methods=['DELETE'])

    def _add_url_rule(self, route, endpoint, func, **kwargs):
        self.routes.append((route, 'users:' + endpoint, func, kwargs))

    def register_routes(self, app):
        for route, endpoint, func, kwargs in self.routes:
            logger.info(f"adding route '{route}' for endpoint '{endpoint}'")
            app.add_url_rule(route, endpoint, self.inject_identity(func), **kwargs)

    def inject_identity(self, wrapped):
        @wraps(wrapped)
        def wrapper(*args, **kwargs):
            bearer = self.get_bearer_from_request()
            (identity, persona) = self.store.decode_identity(bearer)
            logger.debug(f"injecting '{identity}' and '{persona}'")
            return wrapped(*args, identity=identity, persona=persona, **kwargs)
        return wrapper

    def get_bearer_from_request(self, payload=None):
        bearer = request.headers.get('X-Bearer')
        if bearer:
            return bearer
        bearer = request.cookies.get('bearer')
        if bearer:
            return bearer
        if not request.data:
            return 'no-bearer'
        payload = payload or request.get_json(force=True)
        return payload.get('bearer', 'no-bearer')

    def login(self, payload=None, **kwargs):
        payload = payload or request.get_json(force=True)
        try:
            bearer = self.store.authenticate_password(**payload)
            response = make_response(jsonify(dict(bearer=bearer)))
            response.set_cookie('bearer', bearer)
            return response
        except NotFoundError as error:
            abort(404, error)
        except ValueError as error:
            abort(403, error)

    def signin(self, payload=None, **kwargs):
        payload = payload or request.get_json(force=True)
        try:
            bearer = self.store.authenticate_signature(**payload)
            response = make_response(jsonify(dict(bearer=bearer)))
            response.set_cookie('bearer', bearer)
            return response
        except NotFoundError as error:
            abort(404, error)
        except ValueError as error:
            abort(403, error)

    def check_bearer(self, payload=None, **kwargs):
        payload = payload or request.get_json(force=True)
        try:
            bearer = payload.get('bearer', 'no-bearer')
            return jsonify(self.store.check_bearer(bearer=bearer))
        except jwt.exceptions.DecodeError:
            abort(403, "Token cannot be decoded")
        except jwt.exceptions.InvalidSignatureError as error:
            abort(403, error)

    def renew_bearer(self, payload=None, **kwargs):
        payload = payload or request.get_json(force=True)
        try:
            previous = payload.get('bearer', 'no-bearer')
            bearer = self.store.renew_bearer(bearer=previous)
            response = make_response(jsonify(dict(bearer=bearer)))
            response.set_cookie('bearer', bearer)
            return response
        except ValueError as error:
            abort(403, error)

    def index(self, persona='anonymous', **kwargs):
        if not self.permissions.authorize(scope='access-identities',
                                          persona=persona,
                                          topic='list'):
            abort(403, f"Persona '{persona}' can not list identities")
        return self.page(token=None, persona=persona, **kwargs)

    def _filter_attributes(self, record):
        filtered = {k: record[k] for k in record.keys() - self.secret_attributes}
        return filtered

    def _filter_records(self, source, persona='anonymous'):
        permitted = dict(anonymous=[],
                         registered=[],
                         member=['member', 'leader', 'audit'],
                         leader=['registered', 'member', 'leader', 'support', 'audit'],
                         support=['registered', 'member', 'leader', 'support', 'robot', 'audit'],
                         robot=[],
                         audit=['registered', 'member', 'leader', 'support', 'audit'])

        return [r for r in source if r['persona'] in permitted[persona]]

    def page(self, token=None, persona='anonymous', **kwargs):
        if not self.permissions.authorize(scope='access-identities',
                                          persona=persona,
                                          topic='list'):
            abort(403, f"Persona '{persona}' can not list identities")
        try:
            chunk = self.store.chunk(token=token, count=self.page_size)
        except ValueError as error:
            abort(404, error)
        next = 'EOF' if chunk.token == 'EOF' else url_for('users:page', token=chunk.token)
        return jsonify({'users': [self._filter_attributes(record) for record in self._filter_records(chunk.records, persona=persona)],
                        'next': next})

    def get(self, id, identity=None, persona='anonymous', **kwargs):
        record = self.store.read(id)
        if record is None:
            abort(404)
        if id == identity and persona != 'robot':
            pass
        elif not self.permissions.authorize(scope='access-identities',
                                            persona=persona,
                                            topic=record['persona']):
            abort(403, f"Persona '{persona}' can not get identity for '{record['persona']}'")
        return jsonify({'user': self._filter_attributes(record)})

    def post(self, payload=None, identity=None, persona='anonymous', **kwargs):
        logger.debug(f"post identity for persona '{persona}'")
        payload = payload or request.get_json(force=True)
        payload.pop('bearer', None)
        if getsizeof(payload) > self.record_maximum_size:
            abort(400, "Record exceeds maximum size")
        self.command(persona=persona, action='post', payload=payload)

        role = payload.get('persona', 'anonymous')
        if role != 'anonymous' and not self.permissions.authorize(scope='manage-identities',
                                                                  persona=persona,
                                                                  topic=role):
            abort(403, f"Persona '{persona}' can not create identity with role '{role}'")

        id = payload.get('id', None) or payload.get('e_mail', None)
        if not id:
            abort(400, "Please provide and id or an e-mail")
        record = self.store.read(id)
        if record:
            abort(409, "This identity already exists")

        try:
            id = self.store.write(**payload)
        except ValueError as error:
            abort(400, error)
        return '', 201, {'Location': f"/users/{id}"}

    def put(self, id, payload=None, identity=None, persona='anonymous', **kwargs):
        if not id:
            abort(400, "Please provide an id")

        logger.debug(f"put identity ‘{id}’ for persona '{persona}'")
        payload = payload or request.get_json(force=True)
        if getsizeof(payload) > self.record_maximum_size:
            abort(400, "Record exceeds maximum size")
        payload = copy.deepcopy(payload)
        payload['id'] = id
        payload.pop('bearer', None)
        self.command(persona=persona, action='put', payload=payload)

        role = payload.get('persona', None)
        if role is not None:
            if not self.permissions.authorize(scope='manage-identities',
                                              persona=persona,
                                              topic=f'update-any-to-{role}'):
                abort(403, f"Persona '{persona}' can not change identity role to '{role}'")

        if id == identity:
            if not self.permissions.authorize(scope='manage-identities',
                                              persona=persona,
                                              topic='update-self'):
                abort(403, f"Persona '{persona}' can not change own identity '{id}'")
        else:
            record = self.store.read(id)
            if record is None:
                abort(404)
            if not self.permissions.authorize(scope='manage-identities',
                                              persona=persona,
                                              topic=f"update-{record['persona']}-except-role"):
                abort(403, f"Persona '{persona}' can not change identity of role '{record['persona']}'")

        try:
            self.store.write(**payload)
        except ValueError as error:
            abort(400, error)
        return '', 204

    def delete(self, id, identity=None, persona='anonymous', **kwargs):
        if not id:
            abort(400, f"Please provide an id")
        record = self.store.read(id)
        if record is None:
            abort(404)

        logger.debug(f"delete identity ‘{id}’ for persona '{persona}'")
        self.command(persona=persona, action='delete', payload={'id': id})

        if id == identity:
            if not self.permissions.authorize(scope='manage-identities',
                                              persona=persona,
                                              topic='delete-self'):
                abort(403, f"Persona '{persona}' can not delete own identity '{id}'")
        else:
            if not self.permissions.authorize(scope='manage-identities',
                                              persona=persona,
                                              topic=f"delete-{record['persona']}"):
                abort(403, f"Persona '{persona}' can not delete identities")

        self.store.delete(id)
        return '', 204

    def command(self, persona, action, payload, emitter=None):
        emitter = emitter or self.emitter
        if emitter:
            emitter(persona=persona,
                    scope='identities',
                    action=action,
                    payload=payload)

    def replay(self, scope, persona, action, payload, stamp=None):
        if scope != 'identities':
            return
        if stamp:
            if self.replay_stamp and stamp < self.replay_stamp:
                return
            self.replay_stamp = stamp
        if action == 'post':
            self.post(payload=payload, persona=persona)
        elif action == 'put':
            self.put(id=payload['id'], payload=payload, persona=persona)
        elif action == 'delete':
            self.delete(id=payload['id'], persona=persona)
