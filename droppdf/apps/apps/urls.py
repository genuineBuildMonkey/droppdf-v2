from django.urls import path
from django.urls import include

urlpatterns = [path('', include('apps.apps.annotator.urls')),
        path('', include('apps.apps.video.urls'))
        ]
