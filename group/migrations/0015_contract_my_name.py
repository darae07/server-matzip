# Generated by Django 3.2.4 on 2021-07-17 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0014_auto_20210715_1550'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='my_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
