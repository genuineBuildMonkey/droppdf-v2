import re
import io
import binascii

from django.shortcuts import render

from django_http_exceptions import HTTPExceptions

from sanitize_filename import sanitize

from pdfrw import PdfReader, PdfWriter


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

        if ext.lower() != 'pdf':
            raise HTTPExceptions.NOT_ACCEPTABLE #Error code 406

        #make save directory 
        rand_path = randomword(9)
        fingerprint_dir = os.path.join('/tmp/', rand_path)

        os.makedirs(fingerprint_dir)

        filename = sanitize(filename)

        filename = filename.replace("'", '').replace('"', '')
        filename = re.sub(r"[\(,\),\s]+", "-", filename)
        filename = re.sub(r'[^\x00-\x7F]+','.', filename)

        file_content = pdf_file.read()

        content = PdfReader(io.BytesIO(file_content))

        if content.ID is None:
            file_id = 'No ID'
        else:
            file_id = str(content.ID[0]).replace('<', '').replace('>', '')\
                    .replace('(', '').replace(')', '')


        #bad file_ids can contain strange characters
        try:
            file_id.encode('utf-8').strip()
        except UnicodeDecodeError:
            file_id = 'Unreadable'

        file_info = {'filename': pdf_file.name, 'size': pdf_file.size, 'id': file_id, 'directory_name': rand_path}

        for copy_index in range(copy_count):
            if suffix and suffix != '':
                save_filename = filename + '-' + suffix + '-' + str(copy_index + 1) + extension
            else:
                save_filename = filename + '-' + str(copy_index + 1) + extension

            file_path = os.path.join(fingerprint_dir, save_filename)

            #static_link = os.path.join('/pdf', save_filename)
            download_link = os.path.join('/fingerprinter/download/', save_filename)

            content = PdfReader(io.BytesIO(file_content))

            #add some random meta data
            content.Info.randomMetaData = binascii.b2a_hex(os.urandom(20)).upper()

            #change id to random id
            md = hashlib.md5(filename)
            md.update(str(time.time()))
            md.update(os.urandom(10))

            new_id = md.hexdigest().upper()

            #keep length 32
            new_id = new_id[0:32]

            while len(new_id) < 32:
                new_id += random.choice('0123456789ABCDEF')

            content.ID = [new_id, new_id]

            PdfWriter(file_path, trailer=content).write()

            #copy file into online annotator with unique name
            annotation_name = filename + '-' + suffix + '-' \
                    + str(copy_index + 1) + '-' + rand_path + extension

            annotation_path = os.path.join(settings.BASE_DIR, settings.STATIC_ROOT,
                    'drop-pdf', annotation_name)

            shutil.copy(file_path, annotation_path)

            #For some reason nested directories do not provide files from static.
            #We need to clean up double "settings" file and sanify the basic setup but
            #For now serve the file from a dedicated URL.

            copy_info = {'filename': save_filename,
                    'download_path': os.path.join(rand_path, save_filename),
                    'docdrop_link': annotation_name, 'id': content.ID[0]}

            processed_files.append(copy_info)

    else:
        raise Http404('file not provided')


    data = {'processed_files': processed_files, 'file_info': file_info,
            'archive_name': filename}

    render(request, 'refingerprint_results.html', data)


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
