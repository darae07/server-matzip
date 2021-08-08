# Generated by Django 3.2.4 on 2021-07-25 08:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('group', '0017_alter_company_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contract', to=settings.AUTH_USER_MODEL),
        ),
    ]
