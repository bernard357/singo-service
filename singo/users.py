import bcrypt
import hashlib
import jwt
import logging
from time import time
from shortuuid import uuid

import bearers
from records import Records


logger = logging.getLogger(__name__)


AUTHORIZED_PERSONAS = ['anonymous',     # Alice
                       'registered',    # Roger - self-registered
                       'member',        # Marc - recognized as a member
                       'leader',        # Lea - part of the board
                       'robot',         # Robot - trusted software agent
                       'audit',         # Alfred - trusted observer
                       'support']       # Sylvia - system engineer


class NotFoundError(ValueError):
    pass


class Users(Records):

    def __init__(self,
                 authorized_personas=AUTHORIZED_PERSONAS, **kwargs):

        self.authorized_personas = authorized_personas

        self.set_bearer_secret()
        self.bearer_validity = 60
        self.bearer_renewal = 720

        super().__init__(**kwargs)  # file loading may require bearer_secret

    def set_bearer_secret(self, bearer_secret=None):
        self.bearer_secret = bearer_secret or uuid()
        logger.info(f"using bearer secret '{self.bearer_secret}'")

    def write(self, id=None, **kwargs):
        id = id or kwargs.get('e_mail', None)
        if not id:
            raise ValueError("Please provide an id or an e-mail")
        record = self.records.get(id, {})

        if record.get('persona', None) not in self.authorized_personas:
            if kwargs.get('secret', None) == self.bearer_secret:
                kwargs['persona'] = 'support'
            elif 'persona' not in kwargs:
                kwargs['persona'] = 'registered'

        for (key, value) in kwargs.items():
            if key in self.forbidden_attributes:
                continue
            if key == 'e_mail' and id == record.get('e_mail', None):
                self.delete(id=id)
                id = value
            if key == 'password' and kwargs.get('record_has_been_loaded', False) is False:
                # logger.debug(f"hashing {value}")
                value = hashlib.md5(value.encode('utf-8')).hexdigest()
            if key == 'persona' and value not in self.authorized_personas:
                raise ValueError(f"Invalid persona '{value}'")
            record[key] = value
        record['stamp'] = str(time())
        record.pop('id', None)

        try:

            if record['persona'] != 'robot':
                assert record.get('e_mail', None) is not None, "Please provide an e-mail address"

            if record['persona'] != 'registered':
                assert record.get('password', None) is not None, "Please provide a password"

        except AssertionError as error:
            logger.debug(record)
            raise ValueError(str(error))

        # logger.debug(record)
        self.records.put(id, **record)
        return id

    def authenticate_password(self, id, password, hash_password=True, salt=None, stamp=None, **kwargs):
        if hash_password is True:
            logger.debug(f"hashing {password}")
            password = hashlib.md5(password.encode('utf-8')).hexdigest()
        record = self.read(id)
        if record is None:
            raise NotFoundError(f"Unknown identity '{id}'")
        if password != record['password']:
            logger.debug(password)
            logger.debug(record['password'])
            raise ValueError(f"Incorrect authentication credentials")
        return bearers.encode_bearer(secret=self.bearer_secret,
                                     identity=record['id'],
                                     persona=record['persona'],
                                     first_name=record.get('first_name', ''),
                                     last_name=record.get('last_name', ''),
                                     e_mail=record.get('e_mail', '-'),
                                     salt=salt,
                                     stamp=stamp)

    def authenticate_signature(self, id, signature, salt, stamp, **kwargs):
        record = self.read(id)
        if record is None:
            raise NotFoundError(f"Unknown identity '{id}'")
        expected = bearers.compute_signature(hash=record['password'],
                                             salt=salt,
                                             stamp=stamp)
        if expected != signature:
            raise ValueError(f"Incorrect authentication credentials")
        return bearers.encode_bearer(secret=self.bearer_secret,
                                     identity=record['id'],
                                     persona=record['persona'],
                                     first_name=record.get('first_name', ''),
                                     last_name=record.get('last_name', ''),
                                     e_mail=record.get('e_mail', '-'),
                                     salt=salt,
                                     stamp=stamp)

    def decode_identity(self, bearer):
        if bearer != 'no-bearer':
            try:
                payload = bearers.decode_bearer(secret=self.bearer_secret,
                                                bearer=bearer)
                return (payload.identity, payload.persona)
            except jwt.exceptions.DecodeError as error:
                logger.debug(error)
        return ('nobody', 'anonymous')

    def check_bearer(self, bearer):
        payload = bearers.decode_bearer(secret=self.bearer_secret,
                                        bearer=bearer,
                                        validity=self.bearer_validity,
                                        renewal=self.bearer_renewal)
        return payload.__dict__

    def renew_bearer(self, bearer):
        payload = bearers.decode_bearer(secret=self.bearer_secret,
                                        bearer=bearer,
                                        validity=self.bearer_validity,
                                        renewal=self.bearer_renewal)
        if not payload.is_renewable:
            raise ValueError("Bearer has expired")
        return bearers.encode_bearer(secret=self.bearer_secret,
                                     identity=payload.identity,
                                     persona=payload.persona)
