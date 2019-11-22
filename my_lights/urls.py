from django.urls import path
from . import views

app_name = 'my_lights'

urlpatterns = [
    path('', views.index, name='index'),
    path('auth', views.AuthView.as_view(), name='auth'),
    path('receive_auth', views.ReceiveAuthResponse.as_view(), name='auth'),
    path('token', views.RetrieveToken.as_view(), name='token'),
]
