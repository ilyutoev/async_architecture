import json
import uuid
import random

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy

from authn.models import Account
from authn.models import Role
from kafka import KafkaProducer
from tracker.models import Task
from tracker.models import Status
from tracker.forms import TaskForm


producer = KafkaProducer(
    bootstrap_servers=settings.KAFKA_URL,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)


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
            event = {
                'event_name': 'TaskCreated',
                'data': {
                    'public_id': task.public_id,
                    'description': task.description,
                }
            }
            producer.send(
                topic=settings.TASKS_STREAM_TOPIC,
                value=event
            )

            event = {
                'event_name': 'TaskAssigned',
                'data': {
                    'public_id': task.public_id,
                    'account_public_id': task.account.public_id
                }
            }
            producer.send(
                topic=settings.TASKS_TOPIC,
                value=event
            )
            return redirect('/')
        else:
            return render(request, 'add_task.html', {'form': form})


@login_required(login_url=reverse_lazy('login'))
def done_task(request, pk):
    task = Task.objects.get(pk=pk)
    task.status = Status.DONE
    task.save()

    event = {
        'event_name': 'TaskCompleted',
        'data': {
            'public_id': task.public_id,
        }
    }
    producer.send(
        topic=settings.TASKS_TOPIC,
        value=event
    )
    return redirect('/')


@login_required(login_url=reverse_lazy('login'))
def assign_tasks(request):
    accounts = Account.objects.filter(role=Role.WORKER, is_active=True)
    tasks = Task.objects.filter(status=Status.NOT_DONE)

    for task in tasks:
        task.account = random.choice(accounts)
        task.save()
        event = {
            'event_name': 'TaskAssigned',
            'data': {
                'public_id': task.public_id,
                'account_public_id': task.account.public_id
            }
        }
        producer.send(
            topic=settings.TASKS_TOPIC,
            value=event
        )

    return redirect('/')
