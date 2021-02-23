from django.urls import path

from .views import *

urlpatterns = [
        path('', view=home, name='home'),
        path('upload/', view=upload, name="upload"),
        path('pdf/<filename>/', view=pdf, name="pdf"),
        path('csv/<filename>/', view=csv_view, name="csv"),
        ]
