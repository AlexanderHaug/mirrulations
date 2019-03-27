"""This program does the validation of data from
the docs jobs and then creates doc jobs using that data"""

import json
import os
import random
import shutil
import string
import tempfile
import zipfile

import mirrulations_core.documents_core as dc

from mirrulations_core import LOGGER, VERSION

HOME_REGULATION_PATH = os.getenv('HOME') + '/mnt/regulations-data/'
CLIENT_LOG_PATH = os.getenv("HOME") + '/client-logs/'


def process_docs(redis_server, json_data, compressed_file):
    """
    Main documents function, called by the server to compile list of
    document jobs and add them to the "queue" queue
    :param json_data: the json data for the jobs
    :param compressed_file: the zipfile containing the client's log
    :return:
    """
    if redis_server.does_job_exist_in_progress(json_data["job_id"]) is True:
        save_client_log(json_data['client_id'], compressed_file)
        workfile_length_passed = work_file_length_checker(json_data)
        file_type_is_docs = json_data['type'] == 'docs'

        if workfile_length_passed and file_type_is_docs:

            json_data = check_document_exists(json_data)
            add_document_job_to_queue(redis_server, json_data)
            dc.remove_job_from_progress(redis_server, json_data)
        else:
            redis_server.renew_job(json_data['job_id'])


def save_client_log(client_id, compressed_file):
    """
    :param client_id:
    :param compressed_file:
    :return:
    """
    client_path = CLIENT_LOG_PATH + str(client_id) + '/'

    files = zipfile.ZipFile(compressed_file, "r")

    temp_directory = tempfile.mkdtemp()
    temp_directory_path = str(temp_directory + '/')

    files.extractall(temp_directory_path)

    # Create a list of all the files in the directory
    file_list = os.listdir(temp_directory_path)
    for file in file_list:
        if file.endswith('.log'):
            if not os.path.exists(client_path):
                os.makedirs(client_path)
                shutil.copy(temp_directory_path + file, client_path)
            else:
                shutil.copy(temp_directory_path + file, client_path)


def work_file_length_checker(json_data):
    """
        Checks the file count and attachment count of each work file
        :param json_data: the json containing the work files
        :return: True if there are 1000 or less document ids and 1000
                 or less attachments per work file False if either
                 the ids or attachments are over 1000
        """
    file_count = 0
    attachment_count = 0
    for work_file in json_data['data']:
        for line in work_file:
            file_count += 1
            attachment_count += line["count"]

        is_file_count_too_big = file_count > 1000
        is_attachment_count_too_big = attachment_count > 1000
        if is_file_count_too_big or is_attachment_count_too_big:
            return False

        LOGGER.warning('Work file length check completed')
        return True


def check_document_exists(json_data, path=HOME_REGULATION_PATH):
    """
    Checks to see if a document was already downloaded or
        already in one of the queues.
    If the document has already been downloaded
        it will be removed from its workfile.
    If a workfile were to become empty it will be removed
        to prevent empty doc jobs from existing.
    """
    for work_file in json_data["data"]:
        count = 0
        for line in work_file:
            document = line['id']
            alpha_doc_org, docket_id, document_id = \
                dc.get_doc_attributes(document)
            full_path = \
                path + alpha_doc_org + '/' + docket_id + '/' + document_id + \
                '/' + 'doc.' + document + '.json'

            count, local_verdict = \
                check_if_file_exists_locally(full_path, count)

            if local_verdict:
                work_file.pop(count)

    json_data = remove_empty_lists(json_data)
    return json_data


def check_if_file_exists_locally(full_path, count):
    """
    Checks to see if the document exists.
    If the document does not, then the counter is increased
    :param count: The current count of the workfile
    :return: Returns the count and True if the file does exist,
             else it will return False
    """
    if os.path.isfile(full_path):
        return count, True
    count += 1
    return count, False


def remove_empty_lists(json_data):
    """
    :param json_data:
    :return:
    """
    json_data['data'] = \
        [workfile for workfile in json_data['data'] if workfile != []]
    return json_data


def add_document_job_to_queue(redis_server, json_data):
    """
    Creates a job for each work file and then adds each job to the "queue"
    :param json_data: the json data containing all the work files
    :return:
    """
    LOGGER.warning('Adding document job to the queue...')

    for work_file in json_data["data"]:
        random_id = \
            ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        job = create_document_job(work_file, random_id)
        redis_server.add_to_queue(job)
        LOGGER.warning('Document job successfully added to queue')


def create_document_job(work_file, job_id):
    """
    Creates a job for the server to provide to clients
    :param work_file: The list of ids for the clients to retrieve
    :param job_id: The id for the job
    :return: A json in the form of a dictionary
    """
    LOGGER.warning('Creating document job...')
    dictionary = {'job_id': job_id,
                  'type': 'doc',
                  'data': work_file,
                  'version': VERSION}
    return json.dumps(dictionary)
