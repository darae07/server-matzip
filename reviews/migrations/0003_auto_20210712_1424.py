# Generated by Django 3.2.4 on 2021-07-12 14:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_auto_20210701_1423'),
    ]

    operations = [
        migrations.RenameField(
            model_name='review',
            old_name='store_id',
            new_name='store',
        ),
        migrations.RenameField(
            model_name='review',
            old_name='user_id',
            new_name='user',
        ),
    ]
