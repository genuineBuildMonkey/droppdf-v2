from django.db import models

class FileUpload(models.Model):
    '''Reference to cloud upload'''
    filename = models.CharField(max_length=75)

    md5_hash = models.CharField(max_length=64)

    extension = models.CharField(max_length=8)

    is_original = models.BooleanField(default=True)

    parent = models.ForeignKey('FileUpload', on_delete=models.CASCADE,
            null=True, default=None)

    created = models.DateTimeField(auto_now=False, auto_now_add=True)

    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'apps_fileupload'
