# Generated by Django 3.2.4 on 2021-12-12 13:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0009_alter_invite_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invite',
            name='party',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='party', to='group.party'),
        ),
    ]
