from django.contrib.auth.models import AbstractUser
from django.db import models

from accounts.managers import CustomUserManager


class Role(models.TextChoices):
    ADMINISTRATOR = 'admin'
    MANAGER = 'manager'
    ACCOUNTANT = 'accountant'
    WORKER = 'worker'


class Account(AbstractUser):
    public_id = models.CharField(max_length=50)
    role = models.CharField(choices=Role.choices, default=Role.WORKER, max_length=10)
    is_active = models.BooleanField(default=True)

    username = None
    email = models.EmailField('Email address', unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.email
