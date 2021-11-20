# Generated by Django 3.2.9 on 2021-11-14 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0004_alter_task_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='auditlog',
            name='status',
            field=models.CharField(choices=[('task_assigned', 'Task Assigned'), ('task_completed', 'Task Completed'), ('pay_day', 'Pay day')], default='task_assigned', max_length=20),
        ),
    ]