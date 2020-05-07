import logging
from time import time
from yaml import safe_load_all, dump


from customization import c11n


logger = logging.getLogger(__name__)


class Commands:

    def __init__(self, path=None, stream=None):
        self.enabled = True
        if stream:
            self.stream = stream
            self._should_close = False
        else:
            path = path or c11n.commands_file
            logger.info(f"sending commands to '{path}'...")
            self.stream = open(path, 'a')
            self._should_close = True
            self.stream.seek(0)
            self.stream.truncate()

    def __exit__(self, *args, **kwargs):
        if self._should_close:
            self.stream.close()

    def emit(self, persona, scope, action, payload):
        if self.enabled:
            record = self.export(persona=persona, scope=scope, action=action, payload=payload)
            self.stream.write(record)
            self.stream.flush()

    def export(self, persona, scope, action, payload):
        return '---\n' + dump(dict(persona=persona,
                                   scope=scope,
                                   action=action,
                                   payload=payload,
                                   stamp=time()),
                              default_flow_style=False)

    def parse(self, dispatchers=[]):
        logger.debug("parsing commands...")
        self.stream.seek(0)
        for record in safe_load_all(self.stream):
            for dispatcher in dispatchers:
                dispatcher(**record)
