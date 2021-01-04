from django.shortcuts import render
from django.http import HttpResponse, Http404, JsonResponse, HttpResponseNotFound

def save_file(file, path='', extension='pdf'):
    temp = settings.BASE_DIR + settings.STATIC_URL + str(path)

    if not os.path.exists(temp):
        os.makedirs(temp)

    filename = file._get_name()

    #handle non ascii chars in file name
    if isinstance(filename, unicode):
        try:
            filename = unidecode(filename)
        except:
            filename = re.sub(r'[^\x00-\x7F]+','.', filename)

    filename = filename.replace("'", '').replace('"', '')
    filename = re.sub(r"[\(,\),\s]+", "-", filename)

    filename_noextension = '.'.join(filename.split('.')[:-1])
    rand_key = randomword(5)

    filename = filename_noextension + "-" + rand_key + '.' + extension

    fd = open('%s/%s' % (temp, str(filename)), 'wb')
    for chunk in file.chunks():
        fd.write(chunk)
    fd.close()


    if extension == "pdf":
        # get total number of pages 
        page_num = count_pages('%s/%s' % (temp, str(filename)))

        # check if pdf has text.
        os.system("pdftotext " + temp + "/" + str(filename))
        file_text = filename_noextension + "-" + rand_key + '.txt'

        txt_path = temp + "/" + file_text

        if not os.path.exists(txt_path):
            #print 'no text'
            return 'none-' + str(page_num) + "-" + filename
        with open(temp + "/" + file_text, 'rb') as f:
            str_data = f.read()
        os.remove(temp + "/" + file_text)

        if len(str_data) < page_num + 10:
            return 'false-' + str(page_num) + "-" + filename
        return 'true-0-' + filename

    elif extension == 'docx' or extension == 'doc':
        # convert docx to pdf
        pdf_name = filename_noextension + "-" + rand_key + '.pdf'
        pdf_path = '%s/%s' % (temp, str(pdf_name))
        docx_to_pdf('%s/%s' % (temp, str(filename)), pdf_path)

        return 'true-0-' + pdf_name

    elif extension == 'xlsx' or extension == 'xls':
        csv_name = filename_noextension + "-" + rand_key + '.csv'
        csv_path = '%s/%s' % (temp, str(csv_name))

        csv_from_excel('%s/%s' % (temp, str(filename)), csv_path)

        return csv_name

    elif extension == 'csv':
        return filename_noextension + "-" + rand_key + '.csv'

    elif extension == 'epub':
        return filename_noextension + "-" + rand_key + '.epub'


def home(request):
    return render(request, 'index.html', {'request': request})


def upload(request):
    filename = ""
    if request.method == 'POST':
        file_ = request.FILES['file']

        print(file_)

        filename = file_._get_name()

        #temp = filename.split('.')
        #extension = temp[len(temp) - 1]

        #filename = save_file(request.FILES['file'], 'drop-pdf', extension)

    return HttpResponse(filename)
