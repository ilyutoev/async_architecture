import uuid
import random

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy

from authn.models import Account
from authn.models import Role
from tracker.models import Task
from tracker.models import Status
from tracker.forms import TaskForm


@login_required(login_url=reverse_lazy('login'))
def index(request):
    context = {
        'tasks': Task.objects.all(),
        'my_tasks': Task.objects.filter(account=request.user),
        'can_add_task': True if request.user.role in ['manager', 'admin'] else False
    }
    return render(request, 'index.html', context)


@login_required(login_url=reverse_lazy('login'))
def add_task(request):
    if request.method == 'GET':
        is_available_accounts = Account.objects.filter(role=Role.WORKER, is_active=True)
        context = {}
        if is_available_accounts:
            context['form'] = TaskForm()
            context['is_available_accounts'] = True
        else:
            context['is_available_accounts'] = False
        return render(request, 'add_task.html', context)

    elif request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            accounts = Account.objects.filter(role=Role.WORKER, is_active=True)
            task = Task.objects.create(
                public_id=uuid.uuid4(),
                description=form.cleaned_data['description'],
                account=random.choice(accounts)
            )
            # TaskCreated CUD event
            # TaskAssigned BE
            return redirect('/')
        else:
            return render(request, 'add_task.html', {'form': form})


@login_required(login_url=reverse_lazy('login'))
def done_task(request, pk):
    task = Task.objects.get(pk=pk)
    task.status = Status.DONE
    task.save()
    # TaskCompleted BE
    return redirect('/')


@login_required(login_url=reverse_lazy('login'))
def assign_tasks(request):
    accounts = Account.objects.filter(role=Role.WORKER, is_active=True)
    tasks = Task.objects.filter(status=Status.NOT_DONE)

    for task in tasks:
        task.account = random.choice(accounts)
        task.save()
        # BE Taskassigned

    return redirect('/')
