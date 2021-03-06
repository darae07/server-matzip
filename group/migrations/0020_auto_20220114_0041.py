# Generated by Django 3.2.4 on 2022-01-14 00:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0019_party_public'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='location',
            field=models.CharField(default=None, max_length=20),
        ),
        migrations.AddField(
            model_name='teammember',
            name='is_selected',
            field=models.BooleanField(default=True),
        ),
    ]
