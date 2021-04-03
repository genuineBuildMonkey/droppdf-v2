import time
import re
import random

from sanitize_filename import sanitize

from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse

from django.shortcuts import render

from django_http_exceptions import HTTPExceptions

from django.conf import settings

from apps.utils.api_aws import S3

from apps.utils.files import save_temp_file, cleanup_temp_file, check_file_exists, randword


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

        basename = basename[:60]

        new_filename = '{0}-{1}.{2}'.format(basename, randword(5), extension)

        #save to /tmp
        md5_hash, tempfile_path = save_temp_file(new_filename, file_)

        existing_name = check_file_exists(md5_hash)

        if not existing_name:

            s3 = S3(settings.AWS_MEDIA_PRIVATE_BUCKET)

            saved_file = open(tempfile_path, 'rb')

            s3.save_to_bucket(new_filename, saved_file)

            cleanup_temp_file(new_filename)

            return JsonResponse({'existing': False, 'filename': new_filename})

        else:

            cleanup_temp_file(new_filename)

            return JsonResponse({'existing': True, 'filename': existing_name})

        return HttpResponse(new_filename)

    return HttpResponseNotAllowed(['POST,'])
