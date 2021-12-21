# Generated by Django 3.2.4 on 2021-12-11 23:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('group', '0002_team_teammember'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='party',
            name='company',
        ),
        migrations.RemoveField(
            model_name='party',
            name='members',
        ),
        migrations.AddField(
            model_name='party',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='party', to='group.team'),
        ),
        migrations.AlterField(
            model_name='teammember',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='members', to='group.team'),
        ),
        migrations.AlterField(
            model_name='teammember',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='team_membership', to=settings.AUTH_USER_MODEL),
        ),
    ]