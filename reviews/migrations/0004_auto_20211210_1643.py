# Generated by Django 3.2.4 on 2021-12-10 16:43

from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import reviews.models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reviews', '0003_alter_comment_parent_comment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='store',
        ),
        migrations.RemoveField(
            model_name='review',
            name='title',
        ),
        migrations.AddField(
            model_name='review',
            name='address',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='review',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='stores.category'),
        ),
        migrations.AddField(
            model_name='review',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, geography=True, null=True, srid=4326),
        ),
        migrations.AddField(
            model_name='review',
            name='menu',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='review',
            name='price',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='review',
            name='store_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='reviewimage',
            name='image',
            field=models.ImageField(default='', upload_to=reviews.models.unique_path),
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='reviews.review')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
