import time
import re
import random

from sanitize_filename import sanitize

from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse

from django.core.exceptions import SuspiciousFileOperation, ValidationError

from django.shortcuts import render

from django_http_exceptions import HTTPExceptions

from django.conf import settings

from apps.utils.api_aws import S3

from apps.utils.files import save_temp_file, cleanup_temp_file, check_ocr_file_exists,\
        randword, check_pdf_has_text

from apps.models import OCRUpload


def ocr(request):
    return render(request, 'ocr_pdf.html', {})


def upload(request):
    if request.method == 'POST':

        file_ = request.FILES.get('pdf-file')

        processing_error = None

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

        #file already exists in system?
        existing_name = check_ocr_file_exists(md5_hash)

        #already_has_text?
        if check_pdf_has_text(new_filename):
            processing_error = 'This PDF already has text. Use the "Force OCR" button to overwrite text with a fresh OCR if desired. If file was OCRd on previous upload those results will be provided'


        if not existing_name:
            already_exists = False

            #upload original to S3
            s3 = S3(settings.AWS_MEDIA_PRIVATE_BUCKET)

            saved_file = open(tempfile_path, 'rb')

            s3.save_to_bucket(new_filename, saved_file)

            ref = OCRUpload(filename=new_filename, md5_hash=md5_hash, is_original=True)

            ref.save()

            cleanup_temp_file(new_filename)

        else:
            already_exists = True

            cleanup_temp_file(new_filename)

        data = {'file_info': {'filename': filename, 'size': file_.size,
                    'new_filename': new_filename, 'processing_error': processing_error,
                    'tempfile_path': tempfile_path, 'already_exists': already_exists}}

        return JsonResponse(data)

    return HttpResponseNotAllowed(['POST,'])


def result(request):
    if request.method == 'POST':
        #print(request.form.get('file_info'))
        file_info = request.POST.get('file_info')

        if not file_info:
            raise HTTPExceptions.BAD_REQUEST

        print(file_info)

        return HttpResponse('ok')
        #pass

    return HttpResponseNotAllowed(['POST,'])
