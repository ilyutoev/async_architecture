from django.db import models


class Status(models.TextChoices):
    DONE = 'done', 'просо в миске'
    NOT_DONE = 'not_done', 'птичка в клетке'


class AuditLogStatus(models.TextChoices):
    TASK_ASSIGNED = 'task_assigned', 'Task Assigned'
    TASK_COMPLETED = 'task_completed', 'Task Completed'
    PAY_DAY = 'pay_day', 'Pay day'


class Task(models.Model):
    public_id = models.UUIDField()
    description = models.CharField(max_length=255)
    jira_id = models.CharField(max_length=10, null=True)
    account = models.ForeignKey('authn.Account', null=True, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now=True)
    price = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.NOT_DONE)


class AuditLog(models.Model):
    public_id = models.UUIDField()
    account = models.ForeignKey('authn.Account', on_delete=models.PROTECT)
    debit = models.IntegerField(verbose_name='Списание')
    credit = models.IntegerField(verbose_name='Начисление')
    task = models.ForeignKey(Task, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=AuditLogStatus.choices, default=AuditLogStatus.TASK_ASSIGNED)
    created_at = models.DateTimeField(auto_now=True)
