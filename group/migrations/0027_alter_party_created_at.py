# Generated by Django 3.2.4 on 2022-06-14 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0026_crew_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='party',
            name='created_at',
            field=models.DateField(auto_now_add=True, db_index=True, null=True),
        ),
    ]
