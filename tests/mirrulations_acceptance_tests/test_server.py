import pytest
from mirrulations_server.endpoints import app
from mirrulations_server.redis_manager import RedisManager
import json
import os

PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                    "../test_files/mirrulations_files/Archive.zip")


@pytest.fixture
def client():
    app.config['TESTING'] = True
    yield app.test_client()


def test_root_gives_empty_json(client):
    result = client.get('/')
    assert b'{}' == result.data


def test_when_one_job_in_db_then_job_returned_by_get_work(client):
    rm = RedisManager()
    rm.add_to_queue(json.dumps({'job_id': "1234", 'type': "docs", 'data': ["Url1"], 'version': "0.5"}))

    result = client.get('/get_work?client_id=asdf')

    assert b'{"job_id": "1234", "type": "docs", "data": ["Url1"], "version": "0.5"}' == result.data
    assert rm.does_job_exist_in_progress('1234')


def test_when_two_jobs_in_db_returned_by_get_work(client):
    rm = RedisManager()
    rm.add_to_queue(json.dumps({'job_id': "1234", 'type': "docs", 'data': ["Url1"], 'version': "0.5"}))
    rm.add_to_queue(json.dumps({'job_id': "3456", 'type': "docs", 'data': ["Url2"], 'version': "0.5"}))

    result = client.get('/get_work?client_id=asdf')
    result_two = client.get('/get_work?client_id=asdf')

    assert b'{"job_id": "1234", "type": "docs", "data": ["Url1"], "version": "0.5"}' == result.data
    assert b'{"job_id": "3456", "type": "docs", "data": ["Url2"], "version": "0.5"}' == result_two.data
    assert rm.does_job_exist_in_progress('1234')
    assert rm.does_job_exist_in_progress('3456')


def test_when_two_jobs_in_db_return_one_by_get_work(client):
    rm = RedisManager()
    rm.add_to_queue(json.dumps({'job_id': "1234", 'type': "docs", 'data': ["Url1"], 'version': "0.5"}))
    rm.add_to_queue(json.dumps({'job_id': "3456", 'type': "docs", 'data': ["Url2"], 'version': "0.5"}))

    result = client.get('/get_work?client_id=asdf')

    assert b'{"job_id": "1234", "type": "docs", "data": ["Url1"], "version": "0.5"}' == result.data
    assert rm.does_job_exist_in_progress('1234')
    assert rm.does_job_exist_in_queue('3456')
    assert rm.does_job_exist_in_progress('3456') is False


def test_docs_job_in_db_return_doc_place_in_db_queue(client):
    rm = RedisManager()
    rm.add_to_queue(b'{"data": ["Url1"], "version": "v0.5", "type": "docs", "job_id": "1234"}')

    result = client.get('/get_work?client_id=asdf')

    assert b'{"data": ["Url1"], "version": "v0.5", "type": "docs", "job_id": "1234"}' == result.data
    assert rm.does_job_exist_in_progress('1234') is True

    client.post("/return_docs", data={'file': open(PATH, 'rb'), 'json': json.dumps({'job_id': "1234", 'type': 'docs',
                                                          "data": [[{"id": "AHRQ_FRDOC_0001-0036", "count": 1}]],
                                                          'client_id': "abcd",
                                                          "version": "0.5"})})
    assert len(rm.get_all_items_in_queue()) == 1
    assert rm.does_job_exist_in_progress('1234') is False
