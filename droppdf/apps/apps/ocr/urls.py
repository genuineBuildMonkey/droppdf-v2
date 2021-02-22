from django.urls import path, re_path

from .views import *

urlpatterns = [
        path('ocr/', ocr, name='ocr'),
        ]
