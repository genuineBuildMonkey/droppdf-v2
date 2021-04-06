from celery import shared_task
import os

from django.conf import settings

class MaxProcessesExceeded(Exception):
    pass


@shared_task
def ocr_pdf(filename, md5_hash):

    if not os.path.exists('/tmp/ocr_clients'):
        os.makedirs('/tmp/ocr_clients')

    lockfile = os.path.join('/tmp/ocr_clients', md5_hash)

    try:
        #prevent too many heavy ocr processes from running at once
        current_process_count = os.listdir('/tmp/ocr_clients')

        print('XX', type(settings.MAX_SIM_OCR_PROCESSES))

        if current_process_count > settings.MAX_SIM_OCR_PROCESSES:
            raise MaxProcessesExceeded

        f = open(lockfile, 'x')
        f.close()

        os.remove(os.path.join('/tmp/ocr_clients', md5_hash))

    except:
        try:
            os.remove(os.path.join('/tmp/ocr_clients', md5_hash))
        except:
            pass
