# Generated by Django 3.2.4 on 2021-12-13 23:05

from django.db import migrations, models
import group.models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0011_alter_invite_receiver'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='join_code',
            field=models.CharField(default=group.models._create_id, editable=False, max_length=8, unique=True),
        ),
        migrations.AddField(
            model_name='teammember',
            name='image',
            field=models.ImageField(default='', upload_to=group.models.unique_path2),
        ),
        migrations.AddField(
            model_name='teammember',
            name='title',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
