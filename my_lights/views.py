from django.shortcuts import render
from urllib.parse import urlencode
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.views import View
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.urls import reverse_lazy, reverse
import requests
from requests.auth import HTTPBasicAuth
from . import models
import json
from .forms import HueAuthForm, UserProfileForm, UserForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from .helpers import generate_identifier


class IndexView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    redirect_field_name = ''
    template_name = 'my_lights/index.html'


def register(request):
    success_url = reverse_lazy('my_lights:index')
    registered = False

    if request.user.is_authenticated:
        return HttpResponseRedirect(success_url)

    if request.method == "POST":
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            device_id = request.POST['device_id']
            if models.HueAuth.objects.filter(device_id=device_id).exists():
                profile.user_device = models.HueAuth.objects.get(device_id=device_id)
                profile.save()
            else:
                new_device = models.HueAuth.objects.create(device_id=device_id)
                new_device.save()
                profile.user_device = new_device
                profile.save()

            registered = True

        else:
            print(user_form.errors, profile_form.errors)

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'my_lights/register.html', context={'user_form': user_form,
                                                               'profile_form': profile_form,
                                                               'registered': registered})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse_lazy('my_lights:index'))
            else:
                return HttpResponse('Account not active')

        else:
            return HttpResponse('Invalid login details supplied')

    else:
        return render(request, 'my_lights/login.html', {})


@login_required(login_url='/login/')
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse_lazy('my_lights:index'))


class UserLogout(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    redirect_field_name = ''
    template_name = 'my_lights/logout.html'

    def post(self, request, *args, **kwargs):
        if request.POST['logout']:
            logout(request)

        return HttpResponseRedirect(reverse_lazy('my_lights:index'))


class AuthView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = ''
    model = models.HueAuth
    state = generate_identifier()
    print(state)
    params = {
        'state': state,
        'response_type': 'code',

    }
    url = 'https://api.meethue.com/oauth2/auth'
    authBase = models.HueAuthBase.objects.get(app_id='turn_on_my_lights')
    params['clientid'] = authBase.client_id
    params['appid'] = authBase.app_id

    def get(self, request, *args, **kwargs):
        device = request.user.userprofile.user_device
        self.params['deviceid'] = device.device_id
        device.identifier = self.state
        device.save()
        query = urlencode(self.params)
        url = "{}?{}".format(self.url, query)
        return HttpResponseRedirect(url)


class ReceiveAuthResponse(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = ''
    authBase = models.HueAuthBase.objects.get(app_id='turn_on_my_lights')
    success_url = reverse_lazy('my_lights:index')
    get_client_secret_url = reverse_lazy('my_lights:client_secret')
    url = 'https://api.meethue.com/oauth2/token'
    client_id = authBase.client_id
    client_secret = authBase.client_secret

    def get(self, request, *args, **kwargs):
        if 'code' in request.GET:
            identifier = request.GET['state']
            if not models.HueAuth.objects.filter(identifier=identifier).exists():
                return HttpResponseBadRequest(content=b'Bad request!')
            else:
                authObj = models.HueAuth.objects.get(identifier=identifier)
            params = dict()
            params['grant_type'] = 'authorization_code'
            params['code'] = request.GET['code']
            url = '{}?{}'.format(self.url, urlencode(params))
            r = requests.post(url, auth=HTTPBasicAuth(self.client_id, self.client_secret))
            if r.status_code == 200:
                response = json.loads(r.content)
                authObj.access_token = response['access_token']
                authObj.refresh_token = response['refresh_token']
                authObj.save()

                return HttpResponseRedirect(reverse_lazy('my_lights:link'))

            elif r.status_code == 500:
                return HttpResponse('Status code 500. Something went wrong, please try again.')

            else:
                return_string = 'Something went wrong. Please try again\n{}: {}'.format(r.status_code, r.content)
                return HttpResponse(return_string)
        else:
            return HttpResponse('No code received from authentication!')


class LinkView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = ''
    data = {"linkbutton": True}

    def get(self, request, *args, **kwargs):
        url = 'https://api.meethue.com/bridge/0/config'
        headers = {
            'Authorization': 'Bearer ',
            'Content-Type': 'application/json'
        }
        user = request.user
        token = user.userprofile.user_device.access_token
        headers['Authorization'] += token

        data = json.dumps(self.data)
        r = requests.put(url=url, headers=headers, data=data)
        print(headers)

        if r.status_code < 300:
            return render(request, 'my_lights/link.html', {})

        else:
            return_string = 'Something went wrong. Please try again\n{}: {}'.format(r.status_code, r.content)
            return HttpResponse(return_string)

    def post(self, request, *args, **kwargs):
        url = 'https://api.meethue.com/bridge/'
        headers = {
            'Authorization': 'Bearer ',
            'Content-Type': 'application/json'
        }
        user = request.user
        token = user.userprofile.user_device.access_token
        headers['Authorization'] += token
        data = {"devicetype": "turn_on_my_lights"}
        data = json.dumps(data)
        r = requests.post(url=url, headers=headers, data=data)

        # return HttpResponse('Successfully Linked!')

        response = json.loads(r.content)
        print(response)
        response = response[0]
        if 'success' in response:
            if 'username' in response['success']:
                username = response['success']['username']
                device = request.user.userprofile.user_device
                device.user_name_device = username
                device.save()

                return HttpResponse('Device successfully linked!')

        return render(request, 'my_lights/link.html', {'error': 'Link button not pressed. Please try again.'})


