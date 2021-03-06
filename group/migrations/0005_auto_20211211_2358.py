# Generated by Django 3.2.4 on 2021-12-11 23:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0004_membership_team_member'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invite',
            name='receiver',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to='group.teammember'),
        ),
        migrations.AlterField(
            model_name='invite',
            name='sender',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sender', to='group.teammember'),
        ),
    ]
