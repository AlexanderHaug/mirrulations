import fakeredis
import json
import mock

from mirrulations_server.redis_manager import RedisManager, reset_lock, set_lock

from mirrulations_core.documents_core import *


def mock_init(self):
    self.r = fakeredis.FakeRedis()
    reset_lock(self.r)
    self.lock = set_lock(self.r)


@mock.patch('mirrulations_server.redis_manager.reset_lock')
@mock.patch('mirrulations_server.redis_manager.set_lock')
def make_database(reset, lock):
    with mock.patch.object(RedisManager, '__init__', mock_init):
        r = RedisManager()
        r.delete_all()
        return r


def test_get_doc_attributes():
    org, docket, document = get_doc_attributes('mesd-2018-234234-0001')
    assert org == "mesd"
    assert docket == "mesd-2018-234234"
    assert document == "mesd-2018-234234-0001"


def test_get_doc_attributes_multiple_agencies():
    org, docket, document = get_doc_attributes('mesd-abcd-2018-234234-0001')
    assert org == "abcd-mesd"
    assert docket == "mesd-abcd-2018-234234"
    assert document == "mesd-abcd-2018-234234-0001"


def test_get_doc_attributes_special():
    org, docket, document = get_doc_attributes('AHRQ_FRDOC_0001-0001')
    assert org == "AHRQ_FRDOC"
    assert docket == "AHRQ_FRDOC_0001"
    assert document == "AHRQ_FRDOC_0001-0001"


def test_get_doc_attributes_other_special():
    org, docket, document = get_doc_attributes('FDA-2018-N-0073-0002')
    assert org == "FDA"
    assert docket == "FDA-2018-N-0073"
    assert document == "FDA-2018-N-0073-0002"


def test_remove_doc_from_progress():
    redis_server = make_database()

    json_data = json.dumps({'job_id': '1', 'type': 'doc',
                            'client_id': 'Alex', 'VERSION': '0.0.0'})
    redis_server.add_to_progress(json_data)
    json_data = json.loads(json_data)

    remove_job_from_progress(redis_server, json_data)
    progress = redis_server.get_all_items_in_progress()
    assert len(progress) == 0
