import requests

from django.conf import settings
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth import login as account_login

from authn.models import Account


def login(request):
    return render(request, template_name='login.html')


def redirect_to(request):
    oauth_url = f'{settings.AUTH_URL}?' \
                f'response_type=code&' \
                f'client_id={settings.CLIENT_ID}'
    return redirect(oauth_url)


def oauth_callback(request):
    if 'code' in request.GET:
        response = requests.post(
            url='http://127.0.0.1:8001/o/token/',
            data={
                'grant_type': 'authorization_code',
                'client_id': settings.CLIENT_ID,
                'client_secret': settings.CLIENT_SECRET,
                'code': request.GET["code"]
            }
        )

        access_token = response.json()["access_token"]

        response = requests.get(
            url='http://127.0.0.1:8001/accounts/account/',
            headers={
                'Authorization': f'Bearer {access_token}'
            }
        )
        user_data = response.json()

        account = Account.objects.filter(public_id=user_data['public_id']).first()
        if account is None:
            account = Account.objects.create_user(
                email=user_data['email'],
                password=access_token,
                first_name=user_data['first_name'],
                public_id=user_data['public_id'],
                role=user_data['role'],
            )

        account_login(request, account)

    return redirect('/')
