# Generated by Django 3.2.4 on 2022-01-25 00:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0024_auto_20220116_2341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crew',
            name='title',
            field=models.CharField(blank=True, default=None, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='lunch',
            name='crew',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lunches', to='group.crew'),
        ),
        migrations.AlterField(
            model_name='vote',
            name='lunch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='group.lunch'),
        ),
    ]
