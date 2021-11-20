from datetime import date
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.db.models import Sum
from django.shortcuts import render
from django.urls import reverse_lazy

from authn.models import Role
from authn.models import Account
from analitycs.models import AuditLog


@login_required(login_url=reverse_lazy('login'))
def index(request):
    context = {}
    if request.user.role == Role.ADMINISTRATOR:
        context['account'] = Account.objects.filter(
            role=Role.WORKER,
            balance__lt=0
        ).aggregate(account=Sum('balance')).get('account') * -1

        context['expensive_day'] = AuditLog.objects.filter(
            created_at__gt=date.today(),
            task__isnull=False,
        ).aggregate(max=Max('credit')).get('max')

        context['expensive_week'] = AuditLog.objects.filter(
            created_at__gt=date.today() - timedelta(days=7),
            task__isnull=False,
        ).aggregate(max=Max('credit')).get('max')

        context['expensive_month'] = AuditLog.objects.filter(
            created_at__gt=date.today() - timedelta(days=30),
            task__isnull=False,
        ).aggregate(max=Max('credit')).get('max')

    return render(request, 'analytics_index.html', context)
