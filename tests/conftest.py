from fakeredis import FakeRedis, FakeServer
import mock
import pytest
import random
import string
import os

from mirrulations_server.redis_manager import RedisManager,\
                                              set_lock,\
                                              reset_lock


@pytest.fixture(scope='session', autouse=True)
def mock_client_config():
    fake_config_dictionary = {
        'ip': '0.0.0.0',
        'port': '8080',
        'api key': ''.join(random.choices(
            string.ascii_letters + string.digits, k=40)),
        'client id': ''.join(random.choices(
            string.ascii_letters + string.digits, k=16))
    }

    with mock.patch('mirrulations_core.config.client_read_value',
                    side_effect=lambda v: fake_config_dictionary[v]) as f:
        yield f


@pytest.fixture(scope='session', autouse=True)
def mock_server_config():
    self_path = os.path.abspath(os.path.dirname(__file__))
    fake_config_dictionary = {
        'regulations path': os.path.join(self_path, 'test_files/'),
        'client path': os.path.join(self_path, 'tests/'),
        'api key': ''.join(random.choices(
            string.ascii_letters + string.digits, k=40))
    }

    with mock.patch('mirrulations_core.config.server_read_value',
                    side_effect=lambda v: fake_config_dictionary[v]) as f:
        yield f


@pytest.fixture(scope='session', autouse=True)
def mock_web_config():
    self_path = os.path.abspath(os.path.dirname(__file__))
    fake_config_dictionary = {
        'regulations path': os.path.join(self_path, 'test_files/')
    }

    with mock.patch('mirrulations_core.config.web_read_value',
                    side_effect=lambda v: fake_config_dictionary[v]) as f:
        yield f


@pytest.fixture(autouse=True)
def mock_redis_manager():

    fakeredis_server = FakeServer()

    def mock_init(self):
        self.r = FakeRedis(server=fakeredis_server)
        reset_lock(self.r)
        self.lock = set_lock(self.r)

    with mock.patch.object(RedisManager, '__init__', mock_init):
        yield RedisManager()
