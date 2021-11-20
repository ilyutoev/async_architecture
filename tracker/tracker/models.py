from django.db import models


class Status(models.TextChoices):
    DONE = 'done', 'просо в миске'
    NOT_DONE = 'not_done', 'птичка в клетке'


class Task(models.Model):
    public_id = models.UUIDField()
    description = models.CharField(max_length=255)
    jira_id = models.CharField(max_length=10, null=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.NOT_DONE)
    account = models.ForeignKey('authn.Account', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now=True)
