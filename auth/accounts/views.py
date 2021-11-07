import json

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.views import generic
from kafka import KafkaProducer

from accounts.forms import AccountCreationForm, AccountChangeForm
from django.views.generic import DetailView
from django.views.generic import ListView

from accounts.models import Account
from oauth2_provider.views import ProtectedResourceView


producer = KafkaProducer(
    bootstrap_servers=settings.KAFKA_URL,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)


class SignUpView(generic.CreateView):
    form_class = AccountCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

    def form_valid(self, form):
        self.object = form.save()
        event = {
            'event_name': 'AccountCreated',
            'data': {
                'public_id': self.object.public_id,
                'email': self.object.email,
                'role': self.object.role,
                'first_name': self.object.first_name,
            }
        }
        producer.send(
            topic=settings.ACCOUNTS_STREAM_TOPIC,
            value=event
        )

        return super().form_valid(form)


class EditView(generic.UpdateView):
    form_class = AccountChangeForm
    success_url = reverse_lazy('index')
    template_name = 'change.html'
    queryset = Account.objects.all()


class AccountList(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('login')
    redirect_field_name = 'redirect_to'
    queryset = Account.objects.all()
    template_name = 'index.html'


class AccountDelete(DetailView):
    queryset = Account.objects.all()

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        object.is_active = False
        object.save()

        event = {
            'event_name': 'AccountDeleted',
            'data': {'public_id': str(object.public_id)}
        }
        producer.send(
            topic=settings.ACCOUNTS_STREAM_TOPIC,
            value=event
        )

        return redirect(reverse('index'))


class AccountData(ProtectedResourceView):
    def get(self, request, *args, **kwargs):
        data = {
            'public_id': request.resource_owner.public_id,
            'email': request.resource_owner.email,
            'first_name': request.resource_owner.first_name,
            'role': request.resource_owner.role
        }
        return JsonResponse(data)
