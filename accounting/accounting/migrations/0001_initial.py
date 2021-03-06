# Generated by Django 3.2.9 on 2021-11-13 20:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_id', models.UUIDField()),
                ('description', models.CharField(max_length=255)),
                ('jira_id', models.CharField(max_length=10, null=True)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('price', models.IntegerField()),
                ('account', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_id', models.UUIDField()),
                ('debit', models.IntegerField(verbose_name='Списание')),
                ('credit', models.IntegerField(verbose_name='Начисление')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounting.task')),
            ],
        ),
    ]
