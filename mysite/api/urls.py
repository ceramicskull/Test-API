from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/ping', views.ping, name='ping'),
    path('api/posts', views.posts, name='posts'),
]