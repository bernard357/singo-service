from Flask import jsonify, request, abort, url_for
from functools import wraps
import logging
from sys import getsizeof

from permissions import Permissions
from records import Records


logger = logging.getLogger(__name__)


class Channel:
    key_for_record = "item"
    key_for_list = "items"

    def __init__(self, name='', permissions=None, store=None, emitter=None):
        self.name = name or 'universe'
        self.prefix = '' if name == 'universe' else name
        self.permissions = permissions or Permissions(path='fixtures/permissions.yaml')
        self.store = store or Records()
        self.emitter = emitter
        self.replay_stamp = None
        self.record_maximum_size = 1000000
        self.page_size = 10
        self.routes = []
        self._add_url_rule('/', 'index', self.index)
        self._add_url_rule('/page/<token>', 'page', self.page)
        self._add_url_rule('/', 'post', self.post, methods=['POST'])
        self._add_url_rule('/<id>', 'get', self.get)
        self._add_url_rule('/<id>', 'put', self.put, methods=['PUT'])
        self._add_url_rule('/<id>', 'delete', self.delete, methods=['DELETE'])

    def _add_url_rule(self, route, endpoint, func, **kwargs):
        if len(self.prefix):
            route = '/' + self.prefix + route
        self.routes.append((route, self.get_endpoint(endpoint), func, kwargs))

    def get_endpoint(self, endpoint):
        if len(self.prefix):
            return self.key_for_list + ':' + self.prefix + ':' + endpoint
        else:
            return self.key_for_list + ':' + endpoint

    def register_routes(self, app, wrapper=None):
        for route, endpoint, func, kwargs in self.routes:
            if wrapper:
                func = wrapper(func)
            logger.info(f"adding route '{route}' for endpoint '{endpoint}'")
            app.add_url_rule(route, endpoint, func, **kwargs)

    def check_read_permission_decorator(wrapped):
        @wraps(wrapped)
        def wrapper(self, persona='anonymous', **kwargs):
            topic = self.prefix or 'universe'
            if not self.permissions.authorize(scope='access-content',
                                              persona=persona,
                                              topic=topic):
                abort(403, f"Persona '{persona}' can not read channel '{self.name}'")
            return wrapped(self, persona=persona, **kwargs)
        return wrapper

    def check_write_permission_decorator(wrapped):
        @wraps(wrapped)
        def wrapper(self, persona='anonymous', **kwargs):
            topic = self.prefix or 'universe'
            if not self.permissions.authorize(scope='manage-content',
                                              persona=persona,
                                              topic=topic):
                abort(403, f"Persona '{persona}' can not manage channel '{self.name}'")
            return wrapped(self, persona=persona, **kwargs)
        return wrapper

    @check_read_permission_decorator
    def index(self, persona='anonymous', **kwargs):
        logger.debug(f"channel index(persona='{persona}')")
        return self.page(token=None, persona=persona, **kwargs)

    @check_read_permission_decorator
    def page(self, token=None, persona='anonymous', **kwargs):
        logger.debug(f"channel page(persona='{persona}', token='{token}')")
        try:
            chunk = self.store.chunk(token=token, count=self.page_size)
        except ValueError as error:
            abort(404, error)
        next = 'EOF' if chunk.token == 'EOF' else url_for(self.get_endpoint('page'), token=chunk.token)
        return jsonify({self.key_for_list: chunk.records,
                        'next': next})

    @check_read_permission_decorator
    def get(self, id, persona='anonymous', **kwargs):
        record = self.store.read(id)
        if record is None:
            abort(404)
        return jsonify({self.key_for_record: record})

    @check_write_permission_decorator
    def post(self, payload=None, persona='anonymous', **kwargs):
        logger.debug(f"post to channel ‘{self.name}’ for persona '{persona}'")
        payload = payload or request.get_json(force=True)
        payload.pop('bearer', None)
        if getsizeof(payload) > self.record_maximum_size:
            abort(400, "Record exceeds maximum size")
        self.command(persona=persona, action='post', payload=payload)
        id = self.store.write(**payload)
        path = f"/{self.prefix}" if self.prefix else ''
        return '', 201, {'Location': f"{path}/{id}"}

    def _check_version(self, id, payload):
        version = payload.get('version', None)
        previous = payload.get('previous_version', None)
        if version:
            record = self.store.read(id)
            if record is None:
                return version
            current = record.get('version', None)
            if current is not None and current != previous:
                abort(409, "Versions conflict. Please refresh item")
        return version

    @check_write_permission_decorator
    def put(self, id, payload=None, persona='anonymous', **kwargs):
        logger.debug(f"put to channel ‘{self.name}’ for persona '{persona}'")
        if not id:
            abort(400, f"Please provide an id")
        payload = payload or request.get_json(force=True)
        payload['id'] = id
        payload['version'] = self._check_version(id=id, payload=payload)
        payload.pop('bearer', None)
        payload.pop('previous_version', None)
        if getsizeof(payload) > self.record_maximum_size:
            abort(400, "Record exceeds maximum size")
        self.command(persona=persona, action='put', payload=payload)
        self.store.write(**payload)
        return '', 204

    @check_write_permission_decorator
    def delete(self, id, persona='anonymous', **kwargs):
        logger.debug(f"delete in channel ‘{self.name}’ for persona '{persona}'")
        self.command(persona=persona, action='delete', payload={'id': id})
        self.store.delete(id)
        return '', 204

    def command(self, persona, action, payload, emitter=None):
        emitter = emitter or self.emitter
        if emitter:
            emitter(persona=persona,
                    scope=f'channel:{self.name}',
                    action=action,
                    payload=payload)

    def replay(self, scope, persona, action, payload, stamp=None):
        if scope != f'channel:{self.name}':
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
