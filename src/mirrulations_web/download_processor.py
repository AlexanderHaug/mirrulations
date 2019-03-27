import mirrulations_web.directory_search as ds
import mirrulations_web.directory_zip as dz

from mirrulations_web import HOME_REGULATION_PATH


def download_zip(document_id, download_path=HOME_REGULATION_PATH):
    zip_path = ds.search_for_document_in_directory(document_id, download_path)
    if zip_path != '':
        zipfile = dz.zip_directory(document_id, zip_path)
        return zipfile.filename
    else:
        return ''
