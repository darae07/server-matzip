# Generated by Django 3.2.4 on 2021-08-09 23:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='lat',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='store',
            name='lon',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
