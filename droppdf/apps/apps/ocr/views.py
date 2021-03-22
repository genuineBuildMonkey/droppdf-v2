import time
import re
import random
import string

from sanitize_filename import sanitize

from django.http import HttpResponse, HttpResponseNotAllowed 

from django.shortcuts import render

from django_http_exceptions import HTTPExceptions

from apps.utils.tempfiles import save_temp_file, cleanup_temp_file 

def _randomword(length):
       return ''.join(random.choice(string.ascii_lowercase + string.digits)\
               for i in range(length))

def ocr(request):
    return render(request, 'ocr_pdf.html', {})


def upload(request):
    if request.method == 'POST':

        file_ = request.FILES.get('pdf-file')

        if file_ is None:
            raise HTTPExceptions.NOT_ACCEPTABLE #Error code 406

        filename = file_.name

        if not filename or len(filename) < 3 or not '.' in filename:
            raise SuspiciousFileOperation('improper file name')

        filename = sanitize(filename)

        filename = filename.replace("'", '').replace('"', '')
        filename = re.sub(r"[\(,\),\s]+", "-", filename)

        temp = filename.split('.')
        basename = '.'.join(temp[:-1])
        extension = temp[-1]

        if not extension in ('pdf', 'PDF'):
            raise SuspiciousFileOperation('improper file type')

        new_filename = '{0}-{1}.{2}'.format(basename, _randomword(5), extension)

        md5_hash, tempfile_path = save_temp_file(new_filename, file_)

        print(md5_hash)

        #rslt = test_task.delay('paul')
        cleanup_temp_file(new_filename)

        return HttpResponse(new_filename)

    return HttpResponseNotAllowed(['POST,'])
