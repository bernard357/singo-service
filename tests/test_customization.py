import logging
import os
from pytest import mark

from customization import c11n, Customization


pytestmark = mark.wip


def test_default_state_file():
    os.environ['STATE_FILE'] = ''
    assert Customization().state_file == 'fixtures/state.yaml'


def test_state_file_set_by_environ():
    os.environ['STATE_FILE'] = 'fixtures/set_by_environ.yaml'
    assert Customization().state_file == 'fixtures/set_by_environ.yaml'


def test_state_file_set_by_conftest():
    assert c11n.state_file == 'fixtures/test_state.yaml'
