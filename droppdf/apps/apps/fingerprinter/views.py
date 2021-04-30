import re
import io
import os
import random
import hashlib
import time
import string
import binascii

from django.shortcuts import render

from django_http_exceptions import HTTPExceptions

from sanitize_filename import sanitize

from apps.tasks import refingerprint_pdf


def fingerprinter(request):
    return render(request, 'refingerprint.html')


def fingerprinter_upload(request):
    processed_files = []

    pdf_file = request.FILES.get('pdf-file')
    copy_count = request.POST.get('copy-count', 1)
    suffix = request.POST.get('file-suffix', '')
    
    try:
        copy_count = int(copy_count)
    except:
        copy_count = 1

    if pdf_file is not None:

        s = os.path.splitext(pdf_file.name)
        filename = s[0].replace("'", '').replace('"', '')
        extension = s[-1]

        if extension.lower() != '.pdf':
            raise HTTPExceptions.NOT_ACCEPTABLE #Error code 406

        #make save directory 
        rand_path = _randomword(9)
        save_path = os.path.join('/tmp/', rand_path)
        os.makedirs(save_path)

        filename = sanitize(filename)

        filename = filename.replace("'", '').replace('"', '')
        filename = re.sub(r"[\(,\),\s]+", "-", filename)

        save_temp_file(filename, pdf_file, subdir=rand_path)

        data = {'in_process': True, 'directory': rand_path, 'filename': filename}

        return JsonResponse(data)

    else:
        raise Http404('file not provided')


def fingerprinter_download(request, directory_name, filename):
    file_location = os.path.join(settings.BASE_DIR, 'static/fingerprints',
            directory_name, filename)

    try:
        with open(file_location, 'r') as f:
           file_data = f.read()

        response = HttpResponse(file_data, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename

    except IOError:
        response = HttpResponseNotFound('<h1>File does not exist</h1>')

    return response


def fingerprinter_compressed(request, directory_name):
    directory_path = os.path.join(settings.BASE_DIR, 'static/fingerprints',
            directory_name)

    archive_name = request.GET["archive_name"]

    tmp_name = '/tmp/%s' % directory_name
    tmp_zip = tmp_name + '.zip'

    #create zipfile
    content = shutil.make_archive(tmp_name, 'zip', directory_path)

    try:
        with open(tmp_zip, 'rb') as f:
           file_data = f.read()

        response = HttpResponse(file_data, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s.zip"' % archive_name
        os.remove(tmp_zip)

    except IOError:
        response = HttpResponseNotFound('<h1>File does not exist</h1>')

    return response
