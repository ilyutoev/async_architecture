from django.db import models


class Status(models.TextChoices):
    DONE = 'done'
    NOT_DONE = 'not_done'


class Task(models.Model):
    public_id = models.UUIDField()
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.NOT_DONE)
    account = models.ForeignKey('authn.Account', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now=True)
