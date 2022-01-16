# Generated by Django 3.2.4 on 2022-01-16 13:12

from django.db import migrations, models
import group.models_crew


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0020_auto_20220114_0041'),
    ]

    operations = [
        migrations.CreateModel(
            name='Crew',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=None, max_length=100)),
                ('image', models.ImageField(default='', upload_to=group.models_crew.unique_path)),
                ('title', models.CharField(default=None, max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='CrewMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('invite_reason', models.CharField(blank=True, max_length=100, null=True)),
                ('status', models.SmallIntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Lunch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default=None, max_length=300)),
                ('date', models.DateField(auto_now_add=True)),
                ('eat', models.BooleanField(default=False)),
            ],
        ),
        migrations.RemoveField(
            model_name='party',
            name='public',
        ),
        migrations.RemoveField(
            model_name='vote',
            name='party',
        ),
        migrations.RemoveField(
            model_name='vote',
            name='tag',
        ),
        migrations.AddField(
            model_name='party',
            name='eat',
            field=models.BooleanField(default=False),
        ),
    ]