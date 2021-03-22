from celery import shared_task

@shared_task
def ocr_pdf(name):
    print('AAA', name)
