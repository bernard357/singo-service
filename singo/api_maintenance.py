import base64
from flask import jsonify, request, abort
import logging
from yaml import safe_load, dump

from permissions import Permissions


logger = logging.getLogger(__name__)


class Maintenance:

    def __init__(self, permissions=None, users=None, channels=None, state_file=None):
        self.permissions = permissions or Permissions(path='fixtures/permissions.yaml')
        self.users = users
        self.channels = channels
        self.state_file = state_file or 'fixtures/state.yaml'
        if state_file:
            try:
                with open(state_file, 'r') as stream:
                    logger.info(f"loading '{state_file}'...")
                    self.import_content(stream)
            except FileNotFoundError:
                logger.warning(f"can not load '{state_file}'")
        self.routes = []
        self._add_url_rule('/ping', 'ping', self.ping, methods=['GET', 'POST'])
        self._add_url_rule('/snapshot', 'snapshot', self.snapshot, methods=['GET', 'POST'])
        self._add_url_rule('/restore', 'restore', self.restore, methods=['POST'])

    def _add_url_rule(self, route, endpoint, func, **kwargs):
        self.routes.append((route, 'maintenance:' + endpoint, func, kwargs))

    def register_routes(self, app, wrapper=None):
        for route, endpoint, func, kwargs in self.routes:
            if wrapper:
                func = wrapper(func)
            logger.info(f"adding route '{route}' for endpoint '{endpoint}'")
            app.add_url_rule(route, endpoint, func, **kwargs)

    def ping(self, **kwargs):
        logger.debug('ping')
        return jsonify(dict(message='pong'))

    def snapshot(self, identity='nobody', persona='anonymous', payload=None, **kwargs):
        logger.debug(f"snaphot system for '{identity}' and persona '{persona}'")
        if not self.permissions.authorize(scope='manage-system',
                                          persona=persona,
                                          topic='snapshot'):
            abort(403, f"Persona '{persona}' is not allowed to make a snapshot")
        blob = base64.b64encode(self.export_content().encode()).decode()
        logger.debug(f"sending snapshot...")
        return jsonify(dict(blob=blob))

    def restore(self, identity='nobody', persona='anonymous', payload=None, **kwargs):
        logger.debug(f"restore system for '{identity}' and persona '{persona}'")
        if not self.permissions.authorize(scope='manage-system',
                                          persona=persona,
                                          topic='restore'):
            abort(403, f"Persona '{persona}' is not allowed to restore system")
        payload = payload or request.get_json(force=True)
        content = base64.b64decode(payload['blob'])
        logger.debug(f"pushing data to the backend store...")
        try:
            self.import_content(content)
        except ValueError as error:
            abort(400, error)
        return '', 204

    def export_content(self, stream=None):
        content = {}
        for key in self.channels.keys():
            content[key] = self.channels[key].store.dump()
        snapshot = dict(channels=content, users=self.users.dump())
        return dump(snapshot, stream=stream, default_flow_style=False)

    def import_content(self, stream):
        snapshot = safe_load(stream)
        content = snapshot.get('channels', {})
        for key in self.channels.keys():
            count = self.channels[key].store.load(content.get(key, []), append=False)
            if count:
                logger.info(f"{count} items have been loaded in channel '{key}'")
        count = self.users.load(snapshot.get('users', []), append=False)
        if count:
            logger.info(f"{count} identities have been loaded")
