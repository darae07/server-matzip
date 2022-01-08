# Generated by Django 3.2.4 on 2022-01-05 23:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0015_alter_tag_party'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vote',
            name='membership',
        ),
        migrations.RemoveField(
            model_name='vote',
            name='menu',
        ),
        migrations.RemoveField(
            model_name='vote',
            name='store',
        ),
        migrations.AddField(
            model_name='vote',
            name='party',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='group.party'),
        ),
        migrations.AddField(
            model_name='vote',
            name='tag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='group.tag'),
        ),
        migrations.AddField(
            model_name='vote',
            name='team_member',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='group.teammember'),
        ),
    ]