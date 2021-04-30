from django.urls import path, re_path

from .views import *

urlpatterns = [
        path('fingerprinter/', fingerprinter, name='fingerprinter'),
        path('fingerprinter/upload/', fingerprinter_upload, name='fingerprinter_upload'),
        path('fingerprinter/download/', fingerprinter_download, name='fingerprinter_download'),
        path('fingerprinter/compressed/', fingerprinter_compressed, name='fingerprinter_compressed'),
        ]
