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
from jsonschema import validate
from kafka import KafkaProducer
from tracker.models import Task
from tracker.models import Status
from tracker.forms import TaskForm

from events_schema import schema

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
    context = {}
    context['is_available_accounts'] = Account.objects.filter(role=Role.WORKER, is_active=True).exists()
    if request.method == 'GET':
        if context['is_available_accounts']:
            context['form'] = TaskForm()
        return render(request, 'add_task.html', context)

    elif request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            accounts = Account.objects.filter(role=Role.WORKER, is_active=True)
            task = Task.objects.create(
                public_id=uuid.uuid4(),
                description=form.cleaned_data['description'],
                jira_id=form.cleaned_data['jira_id'],
                account=random.choice(accounts)
            )
            event = {
                'event_name': 'TaskCreated',
                'version': 'v1',
                'data': {
                    'public_id': str(task.public_id),
                    'description': task.description,
                    'jira_id': task.jira_id,
                }
            }
            validate(event, schema[event['version']][event['event_name']])
            producer.send(
                topic=settings.TASKS_STREAM_TOPIC,
                value=event
            )

            event = {
                'event_name': 'TaskAssigned',
                'version': 'v1',
                'data': {
                    'public_id': str(task.public_id),
                    'description': task.description,
                    'jira_id': task.jira_id,
                    'account_public_id': str(task.account.public_id)
                }
            }
            validate(event, schema[event['version']][event['event_name']])
            producer.send(
                topic=settings.TASKS_TOPIC,
                value=event
            )
            return redirect('/')
        else:
            context['form'] = form
            return render(request, 'add_task.html', context)


@login_required(login_url=reverse_lazy('login'))
def done_task(request, pk):
    task = Task.objects.get(pk=pk)
    task.status = Status.DONE
    task.save()

    event = {
        'event_name': 'TaskCompleted',
        'version': 'v1',
        'data': {
            'public_id': str(task.public_id),
        }
    }
    validate(event, schema[event['version']][event['event_name']])
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
            'version': 'v1',
            'data': {
                'public_id': str(task.public_id),
                'description': task.description,
                'jira_id': task.jira_id,
                'account_public_id': str(task.account.public_id)
            }
        }
        validate(event, schema[event['version']][event['event_name']])
        producer.send(
            topic=settings.TASKS_TOPIC,
            value=event
        )

    return redirect('/')
