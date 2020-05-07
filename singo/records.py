import base64
from itertools import islice
import logging
from shortuuid import uuid
from time import time

from store import Store


logger = logging.getLogger(__name__)


class Records:

    def __init__(self,
                 salt='azerty'):

        self.records = Store()
        self.salt = salt  # for pagination tokens
        self.forbidden_attributes = ['bearer', 'secret', 'record_has_been_loaded']

    def _encode_token(self, token):
        return base64.b64encode(bytes(self.salt + str(token), encoding='utf-8')).decode()

    def _decode_token(self, token):
        if token == 'EOF':
            raise ValueError(f"End of file")
        if token is None or token == 'None':
            return 0
        decoded = base64.b64decode(token.encode())
        token = int(decoded[len(self.salt):])
        if token < 1:
            token = 0
        return token

    def chunk(self, token=None, count=10):
        token = self._decode_token(token)
        slice = [x for x in islice(self.records.ids_by('stamp'), token, token + count)]
        actual = len(slice)
        records = [self.records.get(id) for id in slice]
        next = self._encode_token(token + count) if actual == count else 'EOF'

        class Chunk:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)

        return Chunk(records=records, count=actual, token=next)

    def read(self, id):
        return self.records.get(id, None)

    def write(self, id=None, **kwargs):
        id = id or uuid()
        record = self.records.get(id, {})
        for (key, value) in kwargs.items():
            if key not in self.forbidden_attributes:
                record[key] = value
        record['stamp'] = str(time())
        record.pop('id', None)
        self.records.put(id, **record)
        return id

    def delete(self, id):
        self.records.delete(id)

    def count(self):
        return len(self.records.ids())

    def scan(self):
        for id in self.records.ids():
            yield self.records.get(id)

    def dump(self):
        return [x for x in self.scan()]

    def load(self, iterator, append=True):
        if not append:
            self.records = Store()
        count = 0
        for record in iterator:
            record['record_has_been_loaded'] = True
            self.write(**record)
            count += 1
        return count
