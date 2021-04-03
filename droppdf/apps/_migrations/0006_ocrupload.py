# Generated by Django 3.1.4 on 2021-04-03 16:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0005_auto_20210331_2024'),
    ]

    operations = [
        migrations.CreateModel(
            name='OCRUpload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=75)),
                ('md5_hash', models.CharField(max_length=64)),
                ('extension', models.CharField(max_length=8)),
                ('is_original', models.BooleanField(default=True)),
                ('is_forced', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('parent', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='apps.fileupload')),
            ],
            options={
                'db_table': 'apps_ocr_upload',
            },
        ),
    ]
