from django.db import models

# Create your models here.

class FileUload(models.Model):
    '''Reference to cloud upload'''
    filename = models.CharField(max_length=75)

    md5_hash = models.CharField(max_length=25)

    extension = models.CharField(max_length=8)

    created = models.DateTimeField(auto_now=False, auto_now_add=True)

    updated = models.DateTimeField(auto_now=True)
