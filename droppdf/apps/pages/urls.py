from django.urls import path
from django.urls import include

urlpatterns = [path('', include('apps.pages.home.urls'))]
