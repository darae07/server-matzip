# Generated by Django 3.2.4 on 2021-12-13 23:05

import common.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commonuser',
            name='image',
            field=models.ImageField(default='', upload_to=common.models.unique_path),
        ),
    ]
