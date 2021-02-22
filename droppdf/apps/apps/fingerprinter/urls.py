from django.urls import path, re_path

from .views import *

urlpatterns = [
        path('fingerprinter/', fingerprinter, name='fingerprinter'),
        ]
