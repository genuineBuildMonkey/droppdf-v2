from django.shortcuts import render


def ocr(request):
    return render(request, 'ocr_pdf.html', {})


def upload(request):
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

        rslt = test_task.delay('paul')

        return HttpResponse(new_filename)

    return HttpResponseNotAllowed(['POST,'])
