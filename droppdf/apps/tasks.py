from celery import shared_task
import subprocess
import os

from hashlib import md5

from django.conf import settings

from apps.utils.api_aws import S3 
from apps.utils.files import save_temp_file, cleanup_temp_file, check_ocr_file_exists

from apps.models import OCRUpload

class MaxProcessesExceededError(Exception):
    pass

class FileInProcessError(Exception):
    '''raised when file with identical hash is already being processed'''
    pass


@shared_task
def ocr_pdf(filename, parent_id, md5_hash, force_flag):

    if not os.path.exists('/tmp/ocr_clients'):
        os.makedirs('/tmp/ocr_clients')

    lockfile = os.path.join('/tmp/ocr_clients', md5_hash)

    try:
        #prevent too many heavy ocr processes from running at once
        current_process_count = len(os.listdir('/tmp/ocr_clients'))

        print('--', current_process_count, int(settings.MAX_SIM_OCR_PROCESSES), '---')

        if current_process_count >= int(settings.MAX_SIM_OCR_PROCESSES):
            raise MaxProcessesExceededError()

        #add to current process count with file
        try:
            f = open(lockfile, 'x')
            f.close()
        except FileExistsError:
            raise FileInProcessError()

        input_path = os.path.join('/tmp', filename)

        #download file and save 
        s3 = S3(settings.AWS_MEDIA_PRIVATE_BUCKET)

        file_obj = s3.download_fileobj_from_bucket(filename)
        #file_obj.save(input_path)
        with open (input_path, 'wb') as tmpfile:
            tmpfile.write(file_obj.getbuffer())
            
       
        basename = '.'.join(filename.split('.')[:-1])
        if force_flag:
            processed_filename = basename + '_ocr_force.pdf'
            force_flag = True
        else:
            processed_filename = basename + '_ocr.pdf'
            force_flag = False

        output_path = os.path.join('/tmp', processed_filename)

        if force_flag:
            f = '--force-ocr'

        else:
            f = ''

        cmd = '/usr/bin/ocrmypdf {} {} {}'.format(f, input_path, output_path)

        rslt = subprocess.check_output(cmd, shell=True)

        #save to s3 
        with open(output_path, 'rb') as file_:
            s3.save_to_bucket(processed_filename, file_)

            file_.seek(0)

            hash_ = md5(file_.read()).hexdigest()

        #record to db
        ref = OCRUpload(filename=processed_filename, md5_hash=hash_,
                is_original=False, is_forced=force_flag, parent_id=parent_id)

        ref.save()

        #remove from process count 
        os.remove(lockfile)

        cleanup_temp_file(filename)
        cleanup_temp_file(processed_filename)

    except Exception as e:
        print(e)

        try:
            os.remove(os.path.join('/tmp/ocr_clients', md5_hash))
            cleanup_temp_file(filename)
            cleanup_temp_file(processed_filename)
        except:
            pass

        raise e
