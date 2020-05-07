import logging
from yaml import safe_load


logger = logging.getLogger(__name__)


AUTHORIZED_SCOPES = ['access-content',          # navigate a channel
                     'manage-content',          # add, modify, delete a page
                     'access-identities',       # navigate identities
                     'manage-identities',       # change user attributes
                     'manage-system']           # dump and load data


class Permissions:

    def __init__(self,
                 path=None,
                 authorized_scopes=AUTHORIZED_SCOPES):

        self.authorized_scopes = authorized_scopes

        self.statements = set()
        if path:
            logger.info(f"loading permissions from '{path}'...")
            self.load(open(path, 'r'))

    def authorize(self, scope, persona, topic):
        statement = scope + ':' + persona + ':' + topic
        return statement in self.statements

    def count(self):
        return len(self.statements)

    def grant(self, scope, persona, topic):
        if scope not in self.authorized_scopes:
            raise ValueError(f"Unauthorized scope '{scope}'")
        self.statements.add(scope + ':' + persona + ':' + topic)

    def grant_all(self, scope, items):
        for item in items:
            if item.get('persona', None):
                self.grant(scope=scope,
                           persona=item['persona'],
                           topic=item['topic'])
            if item.get('personas', None):
                for persona in item['personas']:
                    self.grant(scope=scope,
                               persona=persona,
                               topic=item['topic'])

    def load(self, stream):
        data = safe_load(stream)
        for key in data.keys():
            self.grant_all(scope=key, items=data[key])
