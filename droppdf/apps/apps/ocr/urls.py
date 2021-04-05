from django.urls import path, re_path

from .views import *

urlpatterns = [
        path('ocr/', ocr, name='ocr'),
        path('ocr/upload', upload, name='ocr_upload'),
        path('ocr/result', result, name='ocr_result'),
        ]
