import pytest
import requests_mock
import tempfile
import os
import mirrulations.doc_filter as df


PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../tests/test_files/mirrulations_files/")

@pytest.fixture
def mock_req():
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture()
def workfile_tempdir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


@pytest.fixture()
def savefile_tempdir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


# General Tests
def test_get_document_id():
    assert df.get_document_id('doc.mesd-2018-234234-0001.json') == "mesd-2018-234234-0001"


def test_get_document_id_special():
    assert df.get_document_id('doc.AHRQ_FRDOC_0001-0036.json') == "AHRQ_FRDOC_0001-0036"


def test_get_document_id_other_special():
    assert df.get_document_id('doc.FDA-2018-N-0073-0002.json') == "FDA-2018-N-0073-0002"


def test_get_file_name():
    assert df.get_file_name(PATH + 'doc.mesd-2018-234234-0001.json') == "doc.mesd-2018-234234-0001.json"


# Validation Tests
def test_is_document_ending_a_number():
    assert df.document_id_ending_is_number("FDA-2018-N-0073-0002") is True


def test_is_document_ending_a_number_special():
    assert df.document_id_ending_is_number("AHRQ_FRDOC_0001-0036") is True


def test_is_document_ending_a_word():
    assert df.document_id_ending_is_number("FDA-2018-N-0073-Abcd") is False


def test_is_document_ending_a_word_special():
    assert df.document_id_ending_is_number("AHRQ_FRDOC_0001-WXyz") is False


def test_id_matches_good():
    assert df.document_id_matches_json_id(PATH + "doc.FMCSA-1997-2350-21654.json", "FMCSA-1997-2350-21654") is True


def test_id_matches_bad():
    assert df.document_id_matches_json_id(PATH + "doc.FMCSA-1997-2350-21653.json", "FMCSA-1997-2350-21653") is False


def test_is_document_beginning_good():
    assert df.document_id_beginning_is_letter("AHRQ_FRDOC_0001-0036") is True


def test_is_document_beginning_bad():
    assert df.document_id_beginning_is_letter("9147_FRDOC_0001-0036") is False


# Saving Tests
def test_get_file_list(workfile_tempdir, savefile_tempdir):
    compressed_file = PATH + "Archive.zip"
    PATHstr = savefile_tempdir
    file_list = df.get_file_list(compressed_file, PATHstr + "/", '123')
    assert len(file_list[0]) == 4


def test_get_file_list_and_work(workfile_tempdir, savefile_tempdir):
    compressed_file = PATH + "Archive.zip"
    PATHstr = savefile_tempdir
    file_list = df.get_file_list(compressed_file, PATHstr + "/", '123')

    condition = True
    for file in file_list[0]:
        document_id = df.get_document_id(file)
        if file.startswith("doc.") and df.document_id_ending_is_number(document_id) and df.document_id_beginning_is_letter(document_id):
            pass
        else:
            condition = False
            break

    assert condition is True


def test_get_file_list_and_bad_work(savefile_tempdir):
    compressed_file = PATH + "Bad_Archive.zip"
    PATHstr = savefile_tempdir
    file_list = df.get_file_list(compressed_file, PATHstr + "/", '123')

    condition = True
    for file in file_list[0]:
        document_id = df.get_document_id(file)
        if file.startswith("doc.") and df.document_id_ending_is_number(document_id) and df.document_id_beginning_is_letter(document_id):
            pass
        else:
            condition = False

    assert condition is False


def test_get_file_list_and_more_bad_work(savefile_tempdir):
    compressed_file = PATH + "Bad_Middle_Archive.zip"
    PATHstr = savefile_tempdir
    file_list = df.get_file_list(compressed_file, PATHstr + "/", '123')

    condition = True
    for file in file_list[0]:
        document_id = df.get_document_id(file)
        if file.startswith("doc.") and df.document_id_ending_is_number(document_id) and df.document_id_beginning_is_letter(document_id):
            pass
        else:
            condition = False

    assert condition is False


def test_get_file_list_and_bad_number_work(savefile_tempdir):
    compressed_file = PATH + "Bad_Number_Archive.zip"
    PATHstr = savefile_tempdir
    file_list = df.get_file_list(compressed_file, PATHstr + "/", '123')

    condition = True
    for file in file_list[0]:
        document_id = df.get_document_id(file)
        if file.startswith("doc.") and df.document_id_ending_is_number(document_id) and df.document_id_beginning_is_letter(document_id):
            pass
        else:
            condition = False

    assert condition is False


def test_check_if_document_needs_renew():
    assert df.check_if_document_needs_renew('doc.FMCSA-1997-2350-21654.tif', {'type': 'doc'}, PATH) is False


def test_check_if_document_needs_renew_json():
    assert df.check_if_document_needs_renew('doc.FMCSA-1997-2350-21654.json', {'type': 'doc'}, PATH) is False


def test_check_if_document_needs_renew_bad_json():
    assert df.check_if_document_needs_renew('doc.FMCSA-1997-2350-21653.json', {'type': 'doc'}, PATH) is True


def test_save_single_file_locally(workfile_tempdir, savefile_tempdir):
    filename = "doc.FMCSA-1997-2350-21654.json"
    full_path = "/FMCSA/FMCSA-1997-2350/FMCSA-1997-2350-21654/doc.FMCSA-1997-2350-21654.json"

    path = workfile_tempdir + '/' + filename
    with open(path, 'w') as f:
        f.write("Stuff was written here")

    df.save_single_file_locally(path, savefile_tempdir + '/')
    final_path = savefile_tempdir + full_path

    assert os.path.exists(final_path)

