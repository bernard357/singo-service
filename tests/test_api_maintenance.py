import datetime
from flask import Flask
import io
import json
import jwt
import hashlib
import logging
from pytest import fixture, mark, raises as py_raises
from urllib.parse import unquote
import werkzeug

from api_maintenance import Maintenance


def test_init():
    maintenance = Maintenance(state_file='*does*not*exist*.yaml')
