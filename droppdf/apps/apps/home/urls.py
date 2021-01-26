from django.urls import path

from .views import *

urlpatterns = [
        path('', view=home, name='home'),
        path('upload/', view=upload, name="upload"),
        path('pdf/', view=pdf, name="pdf"),
        ]
