from django.urls import path

from common import views

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
]