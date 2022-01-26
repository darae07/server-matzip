# Generated by Django 3.2.4 on 2022-01-16 23:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0023_auto_20220116_2307'),
    ]

    operations = [
        migrations.AddField(
            model_name='crewmembership',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='membership',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='crewmembership',
            name='date_joined',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='membership',
            name='date_joined',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
