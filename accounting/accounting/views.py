from datetime import date
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import Trunc
from django.shortcuts import render
from django.urls import reverse_lazy

from authn.models import Role
from accounting.models import AuditLog


@login_required(login_url=reverse_lazy('login'))
def index(request):
    context = {'is_admin': False}
    if request.user.role in [Role.ADMINISTRATOR, Role.ACCOUNTANT]:
        context['is_admin'] = True
        context['total_today_cost'] = AuditLog.objects.filter(
            created_at__gte=date.today(),
            created_at__lt=date.today() + timedelta(days=1),
            task__isnull=False
        ).aggregate(
            result=Sum('debit') - Sum('credit')
        ).get('result')

        context['statistic'] = AuditLog.objects.filter(
            task__isnull=False,
        ).annotate(
            date=Trunc('created_at', 'day')
        ).values('date').annotate(
            debit=Sum('debit'),
            credit=Sum('credit')
        )
    elif request.user.role == Role.WORKER:
        context['balance'] = request.user.balance
        context['audit_log'] = AuditLog.objects.filter(
            account=request.user
        ).select_related('task')

    return render(request, 'index.html', context)
