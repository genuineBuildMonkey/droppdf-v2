import random, string
import re
import urllib
import os
import subprocess
import csv

from sanitize_filename import sanitize

from django.shortcuts import render

from django.http import HttpResponse, Http404, JsonResponse, HttpResponseNotFound,\
        HttpResponseNotAllowed 

from django.core.exceptions import SuspiciousFileOperation, ValidationError

from django_http_exceptions import HTTPExceptions

from django.conf import settings

from apps.utils.api_aws import S3

#def save_file(file, path='', extension='pdf'):
    #temp = settings.BASE_DIR + settings.STATIC_URL + str(path)

    #if not os.path.exists(temp):
        #os.makedirs(temp)

    #filename = file._get_name()

    ##handle non ascii chars in file name
    #if isinstance(filename, unicode):
        #try:
            #filename = unidecode(filename)
        #except:
            #filename = re.sub(r'[^\x00-\x7F]+','.', filename)

    #filename = filename.replace("'", '').replace('"', '')
    #filename = re.sub(r"[\(,\),\s]+", "-", filename)

    #filename_noextension = '.'.join(filename.split('.')[:-1])
    #rand_key = randomword(5)

    #filename = filename_noextension + "-" + rand_key + '.' + extension

    #fd = open('%s/%s' % (temp, str(filename)), 'wb')
    #for chunk in file.chunks():
        #fd.write(chunk)
    #fd.close()

    #if extension == "pdf":
        ## get total number of pages 
        #page_num = count_pages('%s/%s' % (temp, str(filename)))

        ## check if pdf has text.
        #os.system("pdftotext " + temp + "/" + str(filename))
        #file_text = filename_noextension + "-" + rand_key + '.txt'

        #txt_path = temp + "/" + file_text

        #if not os.path.exists(txt_path):
            ##print 'no text'
            #return 'none-' + str(page_num) + "-" + filename
        #with open(temp + "/" + file_text, 'rb') as f:
            #str_data = f.read()
        #os.remove(temp + "/" + file_text)

        #if len(str_data) < page_num + 10:
            #return 'false-' + str(page_num) + "-" + filename
        #return 'true-0-' + filename

    #elif extension == 'docx' or extension == 'doc':
        ## convert docx to pdf
        #pdf_name = filename_noextension + "-" + rand_key + '.pdf'
        #pdf_path = '%s/%s' % (temp, str(pdf_name))
        #docx_to_pdf('%s/%s' % (temp, str(filename)), pdf_path)

        #return 'true-0-' + pdf_name

    #elif extension == 'xlsx' or extension == 'xls':
        #csv_name = filename_noextension + "-" + rand_key + '.csv'
        #csv_path = '%s/%s' % (temp, str(csv_name))

        #csv_from_excel('%s/%s' % (temp, str(filename)), csv_path)

        #return csv_name

    #elif extension == 'csv':
        #return filename_noextension + "-" + rand_key + '.csv'

    #elif extension == 'epub':
        #return filename_noextension + "-" + rand_key + '.epub'


def _randomword(length):
       return ''.join(random.choice(string.ascii_lowercase + string.digits)\
               for i in range(length))


def _check_pdf_has_text(new_filename):
    '''Check if if pdf has text or is image pdf.
    Use cli tool "pdftotext" from poppler libs.

    An image pdf will usually show some "text" so discard very short results
    after replacing newlines and blank spaces etc. in first 1,000 or so chars'''
    try:
    
        cmd = 'pdftotext "/tmp/{0}" -'.format(new_filename)

        rslt = subprocess.check_output(cmd, shell=True)

        rslt = rslt[:1000].decode('utf-8', 'ignore')
        
        #remove whitespace, newlines etc.
        rslt = re.sub(r'\W', '', rslt)

        if len(rslt) < 3:
            return False

        return True

    except Exception as e:
        #print(e)
        return False


def _save_temp_file(new_filename, file_):
    '''Save file to disk in /tmp directory.
    returns temp file path'''
    tempfile_path = os.path.join('/tmp', new_filename)

    fd = open(tempfile_path, 'wb')

    for chunk in file_.chunks():
        fd.write(chunk)

    fd.close()

    return tempfile_path


def _cleanup_temp_file(new_filename):
    '''Delete temp file from /tmp directory if exists'''
    try:
        tempfile_path = os.path.join('/tmp', new_filename)
        os.remove(tempfile_path)

    except (OSError, FileNotFoundError):
        pass


def home(request):
    return render(request, 'index.html', {'request': request})


def upload(request):
    filename = ""
    if request.method == 'POST':
        file_ = request.FILES['file']

        filename = file_.name

        if not filename or len(filename) < 3 or not '.' in filename:
            raise SuspiciousFileOperation('improper file name')

        filename = sanitize(filename)

        temp = filename.split('.')
        basename = '.'.join(temp[:-1])
        extension = temp[-1]

        new_filename = '{0}-{1}.{2}'.format(basename, _randomword(5), extension)

        #save file to disk temporarily.
        #later it will be deleted after uploading.
        tempfile_path = _save_temp_file(new_filename, file_)


        if extension == 'pdf':
            #check if is an image pdf or if it has text
            if not _check_pdf_has_text(new_filename):
                _cleanup_temp_file(new_filename)
                raise HTTPExceptions.NOT_ACCEPTABLE #Error code 406

        #elif extension == 'csv':


        s3 = S3(settings.AWS_MEDIA_PRIVATE_BUCKET)

        saved_file = open(tempfile_path, 'rb')

        #s3.save_to_bucket(new_filename, file_)
        s3.save_to_bucket(new_filename, saved_file)

        _cleanup_temp_file(new_filename)

        return HttpResponse(new_filename)

    return HttpResponseNotAllowed(['POST,'])


def pdf(request, filename):
    s3 = S3(settings.AWS_MEDIA_PRIVATE_BUCKET)

    url = s3.get_presigned_url(filename)

    return render(request, 'viewer.html', {'pdf_url': url})


def csv_view(request, filename):
    s3 = S3(settings.AWS_MEDIA_PRIVATE_BUCKET)

    file_obj = s3.download_fileobj_from_bucket(filename)

    csv_data = file_obj.getvalue().decode('utf-8', 'ignore')

    reader = csv.reader(csv_data.splitlines())

    full_content = [i for i in reader]

    headers = full_content[0] 

    content = full_content[1:] 

    return render(request, 'csv_table.html', locals())
