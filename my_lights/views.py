from django.shortcuts import render
from urllib.parse import urlencode
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
import requests
from hashlib import md5
from requests.auth import HTTPDigestAuth, HTTPBasicAuth
from . import models
import json
from .forms import HueAuthForm

class AuthData:
    CLIENT_ID = 'zI0dBLsG8CeWT2o7wxRb1YGxeb1ALeNd'
    CLIENT_SECRET = 'wef'
    ACCESS_TOKEN = "l5JA5TArOuoylVetTWL8G8SSWJhg"
    REFRESH_TOKEN = "bM9UTpAYl5aG7Oj5zFKigitgL4KJ5QGx"
    BASE_URL = "https://api.meethue.com/bridge/NGTuf-IseVRZt68DWsdqaZcZ6IuHjv3zXARXT6LD"


def index(request):
    return HttpResponse("<a href='http://localhost:8000/auth'>Auth</a>")


def join_and_hash(string_list):
    encode_string = ':'.join(string_list)
    encode_string = encode_string.encode('utf-8')
    hashed = md5(encode_string)
    return hashed.hexdigest()




class AuthView(FormView):
    model = models.HueAuth
    form_class = HueAuthForm
    template_name = 'my_lights/hue_auth_form.html'
    params = {
        'state': 'test',
        'response_type': 'code',
    }
    url = 'https://api.meethue.com/oauth2/auth'

    def form_valid(self, form):

        self.params.update(form.cleaned_data)
        print(form.cleaned_data)
        print(self.params)

        form.save()
        query = urlencode(self.params)
        print(query)
        url = "{}?{}".format(self.url, query)
        print(url)
        return HttpResponseRedirect(url)



    # def get(self, request, *args, **kwargs):
    #     query = urlencode(self.params)
    #     url = "{}?{}".format(self.url, query)
    #     return HttpResponseRedirect(url)


class ReceiveAuthResponse(View):
    success_url = reverse_lazy('my_lights:index')
    get_client_secret_url = reverse_lazy('my_lights:client_secret')
    url = 'https://api.meethue.com/oauth2/token'
    client_id = AuthData.CLIENT_ID
    client_secret = AuthData.CLIENT_SECRET

    def get(self, request, *args, **kwargs):
        if 'code' in request.GET:
            params = dict()
            params['grant_type'] = 'authorization_code'
            params['code'] = request.GET['code']
            url = '{}?{}'.format(self.url, urlencode(params))
            r = requests.post(url, auth=HTTPBasicAuth(self.client_id, self.client_secret))
            print(r)
            print(r.content)
            if r.status_code == 200:
                response = json.loads(r.content)
                AuthData.ACCESS_TOKEN = response['access_token']
                AuthData.REFRESH_TOKEN = response['refresh_token']

                return HttpResponseRedirect(self.success_url)

            elif r.status_code == 500:
                return

            else:
                print(r.status_code)
                print(r.content)

            # return HttpResponse('<h1>Authentication code:<h/1><br><code>{}</code>'.format(params['code']))

        else:
            return HttpResponse('No code received from authentication!')




class RetrieveToken(View):
    success_url = reverse_lazy('my_lights:index')




