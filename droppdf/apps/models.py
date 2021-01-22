from django.db import models

# Create your models here.

class FileUload(models.Model):
    '''reference to cloud upload'''
    name = models.CharField(max_length=35)

    url = models.CharField(max_length=50)

    extension = models.CharField(max_length=8)

    created = models.DateTimeField(auto_now=False, auto_now_add=True)

    updated = models.DateTimeField(auto_now=True)
