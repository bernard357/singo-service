import datetime
import hashlib
import hmac
import jwt
import logging
from shortuuid import uuid


logger = logging.getLogger(__name__)


def get_salt():
    return str(uuid())


def get_current_stamp():
    return datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')


def get_stamp(delta=0):
    if delta < 0:
        return datetime.datetime.utcnow() + datetime.timedelta(minutes=delta)
    else:
        return datetime.datetime.utcnow() + datetime.timedelta(minutes=delta)


def stamp_is_valid(stamp, validity=60):
    ''' Ensure stamp is neither expired nor futuristic '''

    # date of signature is UTC
    bearer_stamp = datetime.datetime.strptime(stamp, '%Y%m%dT%H%M%SZ')

    # future stamps are not accepted
    if bearer_stamp > get_stamp(delta=5):
        return False

    # signatures are not valid after some time
    if bearer_stamp < get_stamp(delta=-validity):
        return False

    return True


def encode_bearer(secret, identity, persona, salt=None, stamp=None, **kwargs):
    salt = get_salt() if salt is None else salt
    stamp = get_stamp().strftime('%Y%m%dT%H%M%SZ') if stamp is None else stamp
    payload = dict(identity=identity,
                   persona=persona,
                   salt=salt,
                   stamp=stamp,
                   **kwargs)
    bearer = jwt.encode(payload, secret, algorithm='HS256').decode()
    return bearer


def decode_bearer(secret, bearer, validity=60, renewal=720):
    if secret is None:
        payload = jwt.decode(bearer.encode(), verify=False)  # for tests only
    else:
        payload = jwt.decode(bearer.encode(), secret, algorithms=['HS256'])
    if payload.get('salt', None) is None:
        raise ValueError("Missing salt field in the payload")
    if payload.get('stamp', None) is None:
        raise ValueError("Missing stamp field in the payload")
    payload['is_valid'] = stamp_is_valid(stamp=payload['stamp'], validity=validity)
    payload['is_renewable'] = stamp_is_valid(stamp=payload['stamp'], validity=renewal)

    class Payload:
        def __init__(self, **kwargs):
            self.__dict__.update(**kwargs)

    # logger.debug("bearer: \n" + str(payload))
    return Payload(**payload)


def compute_signature(hash, salt, stamp):
    message = hash + '\n' + salt
    blob = hmac.new(stamp.encode('utf-8'),
                    message.encode('utf-8'),
                    hashlib.sha256).hexdigest()
    logger.debug(f"computed signature from hash {hash} salt {salt} stamp {stamp}\n" + str(blob))
    return blob
