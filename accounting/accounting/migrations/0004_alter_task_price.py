# Generated by Django 3.2.9 on 2021-11-14 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0003_task_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='price',
            field=models.IntegerField(default=0),
        ),
    ]
