# Generated by Django 3.2.4 on 2022-07-03 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0003_keyword_good_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='keyword',
            name='use_kakaomap',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='keyword',
            name='use_team_location',
            field=models.BooleanField(default=True),
        ),
    ]
