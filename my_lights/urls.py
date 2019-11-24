from django.urls import path
from . import views
from django.contrib.auth.views import auth_login, auth_logout

app_name = 'my_lights'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('auth/', views.AuthView.as_view(), name='auth'),
    path('receive_auth/', views.ReceiveAuthResponse.as_view(), name='receive_auth'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.UserLogout.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('link/', views.LinkView.as_view(), name='link'),
]
