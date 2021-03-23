import os
import string

from apps.models import FileUload

from hashlib import md5


def save_temp_file(new_filename, file_):
    '''Save file to disk in /tmp directory.
    returns tuple(md5 hash, temp file path)'''
    tempfile_path = os.path.join('/tmp', new_filename)

    hash_ = md5()

    fd = open(tempfile_path, 'wb')

    for chunk in file_.chunks():
        hash_.update(chunk)

        fd.write(chunk)

    fd.close()

    return (hash_.hexdigest(), tempfile_path)


def cleanup_temp_file(new_filename):
    '''Delete temp file from /tmp directory if exists'''
    try:
        tempfile_path = os.path.join('/tmp', new_filename)
        os.remove(tempfile_path)

    except (OSError, FileNotFoundError):
        pass


def check_file_exists(md5_hash):
    '''Check database for hash.
    Return filename if exists, otherwise False'''

    pass


def file_record_db(md5_hash, filename):
    pass


def randword(length):
       return ''.join(random.choice(string.ascii_lowercase + string.digits)\
               for i in range(length))
